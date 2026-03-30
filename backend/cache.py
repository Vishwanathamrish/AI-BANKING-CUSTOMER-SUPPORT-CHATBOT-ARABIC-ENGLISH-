"""
Caching Layer - Redis-based caching for improved performance

This module provides:
- Response caching
- Vector search result caching
- Session caching
- Configurable TTL (Time To Live)
"""

import os
import json
import logging
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a cache entry with metadata."""
    
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheEntry':
        """Create from dictionary."""
        entry = cls(
            value=data["value"],
            ttl_seconds=0  # Will be calculated from timestamps
        )
        entry.created_at = datetime.fromisoformat(data["created_at"])
        entry.expires_at = datetime.fromisoformat(data["expires_at"])
        return entry


class InMemoryCache:
    """
    Thread-safe in-memory cache as Redis alternative.
    
    Features:
    - TTL-based expiration
    - LRU eviction
    - Thread safety
    - Statistics tracking
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600
    ):
        """
        Initialize in-memory cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time-to-live in seconds
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        logger.info(f"In-memory cache initialized (max_size={max_size}, default_ttl={default_ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None
            
            # Move to end for LRU (by re-inserting)
            value = entry.value
            self.cache.pop(key)
            self.cache[key] = CacheEntry(value, self.default_ttl)
            
            self.hits += 1
            return value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional)
            
        Returns:
            True if successful
        """
        with self.lock:
            # Evict if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_oldest()
            
            actual_ttl = ttl if ttl is not None else self.default_ttl
            self.cache[key] = CacheEntry(value, actual_ttl)
            return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    def _evict_oldest(self):
        """Evict oldest entry (LRU)."""
        if not self.cache:
            return
        
        # Find oldest entry (first inserted)
        oldest_key = next(iter(self.cache))
        del self.cache[oldest_key]
        self.evictions += 1
        logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired entries")
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "total_entries": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "hit_rate_percent": round(hit_rate, 2),
                "default_ttl_seconds": self.default_ttl
            }
    
    def generate_key(self, prefix: str, *args) -> str:
        """
        Generate cache key from arguments.
        
        Args:
            prefix: Key prefix
            *args: Arguments to hash
            
        Returns:
            Generated cache key
        """
        # Create string from arguments
        args_str = json.dumps(args, sort_keys=True, default=str)
        
        # Generate hash
        hash_obj = hashlib.md5(args_str.encode())
        hash_hex = hash_obj.hexdigest()[:12]
        
        return f"{prefix}:{hash_hex}"


class CachingManager:
    """
    Centralized caching manager for the banking chatbot.
    
    Provides specialized caches for different use cases:
    - Response cache
    - Vector search cache
    - Intent detection cache
    - Session cache
    """
    
    def __init__(self, use_redis: bool = False, redis_url: Optional[str] = None):
        """
        Initialize caching manager.
        
        Args:
            use_redis: Whether to use Redis (not implemented, falls back to memory)
            redis_url: Redis connection URL
        """
        self.use_redis = use_redis
        
        # Initialize caches with different configurations
        self.response_cache = InMemoryCache(max_size=500, default_ttl=1800)  # 30 min
        self.vector_cache = InMemoryCache(max_size=200, default_ttl=3600)  # 1 hour
        self.intent_cache = InMemoryCache(max_size=300, default_ttl=900)  # 15 min
        self.session_cache = InMemoryCache(max_size=1000, default_ttl=7200)  # 2 hours
        
        logger.info("Caching manager initialized")
    
    def get_cached_response(
        self,
        query: str,
        language: str = "en"
    ) -> Optional[Dict]:
        """
        Get cached response for a query.
        
        Args:
            query: User query
            language: Language preference
            
        Returns:
            Cached response or None
        """
        key = self.response_cache.generate_key("response", query, language)
        return self.response_cache.get(key)
    
    def cache_response(
        self,
        query: str,
        response: Dict,
        language: str = "en",
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache a response.
        
        Args:
            query: User query
            response: Response to cache
            language: Language
            ttl: Custom TTL
            
        Returns:
            Success status
        """
        key = self.response_cache.generate_key("response", query, language)
        return self.response_cache.set(key, response, ttl=ttl)
    
    def get_cached_vector_search(
        self,
        query: str,
        k: int = 3
    ) -> Optional[List]:
        """Get cached vector search results."""
        key = self.vector_cache.generate_key("vector", query, k)
        return self.vector_cache.get(key)
    
    def cache_vector_search(
        self,
        query: str,
        results: List,
        k: int = 3,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache vector search results."""
        key = self.vector_cache.generate_key("vector", query, k)
        return self.vector_cache.set(key, results, ttl=ttl)
    
    def get_cached_intent(
        self,
        text: str
    ) -> Optional[tuple]:
        """Get cached intent detection result."""
        key = self.intent_cache.generate_key("intent", text)
        return self.intent_cache.get(key)
    
    def cache_intent(
        self,
        text: str,
        result: tuple,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache intent detection result."""
        key = self.intent_cache.generate_key("intent", text)
        return self.intent_cache.set(key, result, ttl=ttl)
    
    def get_session_data(
        self,
        session_id: str
    ) -> Optional[Dict]:
        """Get cached session data."""
        return self.session_cache.get(f"session:{session_id}")
    
    def set_session_data(
        self,
        session_id: str,
        data: Dict,
        ttl: Optional[int] = None
    ) -> bool:
        """Cache session data."""
        return self.session_cache.set(f"session:{session_id}", data, ttl=ttl)
    
    def invalidate_user_sessions(self, user_id: str):
        """Invalidate all sessions for a user."""
        # This would be more sophisticated with Redis
        logger.info(f"Invalidating sessions for user: {user_id}")
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all caches."""
        return {
            "response_cache": self.response_cache.get_stats(),
            "vector_cache": self.vector_cache.get_stats(),
            "intent_cache": self.intent_cache.get_stats(),
            "session_cache": self.session_cache.get_stats()
        }
    
    def cleanup_all_expired(self):
        """Clean up expired entries in all caches."""
        total_cleaned = 0
        total_cleaned += self.response_cache.cleanup_expired()
        total_cleaned += self.vector_cache.cleanup_expired()
        total_cleaned += self.intent_cache.cleanup_expired()
        total_cleaned += self.session_cache.cleanup_expired()
        
        if total_cleaned > 0:
            logger.info(f"Cleaned up {total_cleaned} expired cache entries")


# Singleton instance
_caching_manager = None


def get_caching_manager(use_redis: bool = False) -> CachingManager:
    """Get or create singleton caching manager instance."""
    global _caching_manager
    if _caching_manager is None:
        _caching_manager = CachingManager(use_redis=use_redis)
    return _caching_manager


def cache_response(query: str, response: Dict, language: str = "en") -> bool:
    """Convenience function to cache response."""
    manager = get_caching_manager()
    return manager.cache_response(query, response, language)


def get_cached_response(query: str, language: str = "en") -> Optional[Dict]:
    """Convenience function to get cached response."""
    manager = get_caching_manager()
    return manager.get_cached_response(query, language)
