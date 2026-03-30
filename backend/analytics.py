"""
Analytics Module - Track conversation metrics and insights

This module provides analytics tracking for:
- Most asked questions
- Response times
- Failed queries
- Language distribution
- Intent statistics
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


class ConversationAnalytics:
    """
    Analytics tracker for conversation metrics.
    
    Tracks:
    - Question frequency
    - Response confidence scores
    - Language distribution
    - Intent distribution
    - Failed queries
    - Average response time
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize analytics tracker.
        
        Args:
            log_dir: Directory to store conversation logs
        """
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "conversation_logs.json")
        self.metrics_file = os.path.join(log_dir, "metrics.json")
        
        # In-memory metrics (for fast access)
        self.question_counts = defaultdict(int)
        self.intent_counts = defaultdict(int)
        self.language_counts = defaultdict(int)
        self.confidence_scores = []
        self.failed_queries = []
        self.response_times = []
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Load existing metrics
        self._load_metrics()
        
        logger.info(f"Analytics initialized. Logs: {log_dir}")
    
    def _load_metrics(self):
        """Load metrics from file if exists."""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    metrics = json.load(f)
                    
                self.question_counts = defaultdict(int, metrics.get('question_counts', {}))
                self.intent_counts = defaultdict(int, metrics.get('intent_counts', {}))
                self.language_counts = defaultdict(int, metrics.get('language_counts', {}))
                self.confidence_scores = metrics.get('confidence_scores', [])
                self.failed_queries = metrics.get('failed_queries', [])
                self.response_times = metrics.get('response_times', [])
                
                logger.info("Loaded existing metrics")
        except Exception as e:
            logger.error(f"Error loading metrics: {e}")
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            metrics = {
                'question_counts': dict(self.question_counts),
                'intent_counts': dict(self.intent_counts),
                'language_counts': dict(self.language_counts),
                'confidence_scores': self.confidence_scores,
                'failed_queries': self.failed_queries,
                'response_times': self.response_times,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def track_conversation(
        self,
        question: str,
        answer: str,
        language: str,
        intent: str,
        confidence: float,
        response_time_ms: float,
        is_fallback: bool = False,
        user_id: Optional[str] = None
    ):
        """
        Track a conversation interaction.
        
        Args:
            question: User's question
            answer: Bot's response
            language: Detected language
            intent: Detected intent
            confidence: Response confidence score
            response_time_ms: Response time in milliseconds
            is_fallback: Whether fallback was used
            user_id: Optional user identifier
        """
        with self.lock:
            # Normalize question for counting (lowercase, strip)
            normalized_question = question.lower().strip()
            
            # Update metrics
            self.question_counts[normalized_question] += 1
            self.intent_counts[intent] += 1
            self.language_counts[language] += 1
            self.confidence_scores.append(confidence)
            self.response_times.append(response_time_ms)
            
            # Track failed queries
            if is_fallback or confidence < 0.5:
                self.failed_queries.append({
                    'question': question,
                    'answer': answer,
                    'confidence': confidence,
                    'intent': intent,
                    'language': language,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Keep only last 1000 entries for memory efficiency
            if len(self.confidence_scores) > 1000:
                self.confidence_scores = self.confidence_scores[-1000:]
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
            if len(self.failed_queries) > 100:
                self.failed_queries = self.failed_queries[-100:]
            
            # Log conversation
            self._log_conversation({
                'question': question,
                'answer': answer,
                'language': language,
                'intent': intent,
                'confidence': confidence,
                'response_time_ms': response_time_ms,
                'is_fallback': is_fallback,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Save metrics periodically
            self._save_metrics()
            
            logger.debug(f"Tracked conversation: intent={intent}, confidence={confidence:.2f}")
    
    def _log_conversation(self, data: Dict):
        """Append conversation to log file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error logging conversation: {e}")
    
    def get_most_asked_questions(self, limit: int = 10) -> List[Dict]:
        """
        Get most frequently asked questions.
        
        Args:
            limit: Number of questions to return
            
        Returns:
            List of questions with counts
        """
        sorted_questions = sorted(
            self.question_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {'question': q, 'count': c}
            for q, c in sorted_questions
        ]
    
    def get_intent_distribution(self) -> Dict[str, int]:
        """Get distribution of intents."""
        return dict(self.intent_counts)
    
    def get_language_distribution(self) -> Dict[str, int]:
        """Get distribution of languages."""
        return dict(self.language_counts)
    
    def get_average_confidence(self) -> float:
        """Get average confidence score."""
        if not self.confidence_scores:
            return 0.0
        
        return sum(self.confidence_scores) / len(self.confidence_scores)
    
    def get_average_response_time(self) -> float:
        """Get average response time in ms."""
        if not self.response_times:
            return 0.0
        
        return sum(self.response_times) / len(self.response_times)
    
    def get_failed_queries(self, limit: int = 20) -> List[Dict]:
        """
        Get recent failed queries.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of failed query details
        """
        return self.failed_queries[-limit:]
    
    def get_summary_statistics(self) -> Dict:
        """
        Get summary statistics for dashboard.
        
        Returns:
            Dictionary with key metrics
        """
        total_conversations = sum(self.question_counts.values())
        
        return {
            'total_conversations': total_conversations,
            'unique_questions': len(self.question_counts),
            'average_confidence': self.get_average_confidence(),
            'average_response_time_ms': self.get_average_response_time(),
            'failed_query_count': len(self.failed_queries),
            'language_distribution': self.get_language_distribution(),
            'intent_distribution': self.get_intent_distribution(),
            'top_questions': self.get_most_asked_questions(5)
        }
    
    def export_analytics(self, output_file: str) -> bool:
        """
        Export full analytics to file.
        
        Args:
            output_file: Output file path
            
        Returns:
            Success status
        """
        try:
            analytics = {
                'exported_at': datetime.now().isoformat(),
                'summary': self.get_summary_statistics(),
                'detailed_metrics': {
                    'question_counts': dict(self.question_counts),
                    'intent_counts': dict(self.intent_counts),
                    'language_counts': dict(self.language_counts),
                    'recent_failures': self.failed_queries[-50:]
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analytics, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Analytics exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting analytics: {e}")
            return False
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        with self.lock:
            self.question_counts.clear()
            self.intent_counts.clear()
            self.language_counts.clear()
            self.confidence_scores.clear()
            self.failed_queries.clear()
            self.response_times.clear()
            
            # Clear log files
            for filepath in [self.log_file, self.metrics_file]:
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            logger.info("Metrics reset")


# Singleton instance
_analytics_tracker = None


def get_analytics_tracker() -> ConversationAnalytics:
    """Get or create singleton analytics instance."""
    global _analytics_tracker
    if _analytics_tracker is None:
        _analytics_tracker = ConversationAnalytics()
    return _analytics_tracker


def track_conversation(**kwargs):
    """Convenience function to track conversation."""
    tracker = get_analytics_tracker()
    return tracker.track_conversation(**kwargs)
