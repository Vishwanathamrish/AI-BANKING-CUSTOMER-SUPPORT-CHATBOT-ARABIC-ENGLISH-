# Multi-stage Dockerfile for Production Banking AI Assistant

# ========================================
# Stage 1: Backend (FastAPI)
# ========================================
FROM python:3.10-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY data/ ./data/
COPY .env.example ./.env

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run backend
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


# ========================================
# Stage 2: Frontend (Next.js)
# ========================================
FROM node:20-alpine as frontend-builder

WORKDIR /app

# Copy package files
COPY frontend/nextjs_chat_ui/package.json ./
COPY frontend/nextjs_chat_ui/pnpm-lock.yaml* ./

# Install dependencies
RUN npm install

# Copy source code
COPY frontend/nextjs_chat_ui/ ./

# Build Next.js application
RUN npm run build


# ========================================
# Stage 3: Frontend Runtime
# ========================================
FROM node:20-alpine as frontend

WORKDIR /app

# Set production environment
ENV NODE_ENV=production

# Copy package files and install only production dependencies
COPY frontend/nextjs_chat_ui/package.json ./
RUN npm install --only=production

# Copy built application from builder stage
COPY --from=frontend-builder /app/.next ./.next
COPY --from=frontend-builder /app/public ./public
COPY --from=frontend-builder /app/next.config.js ./

EXPOSE 3000

# Run Next.js application
CMD ["npm", "start"]


# ========================================
# Stage 4: Combined (Optional - for single container)
# ========================================
FROM python:3.10-slim as combined

WORKDIR /app

# Install Node.js for frontend serving
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/
COPY data/ ./data/

# Copy and build frontend
COPY frontend/nextjs_chat_ui/package.json ./frontend/nextjs_chat_ui/
WORKDIR /app/frontend/nextjs_chat_ui
RUN npm install
RUN npm run build

WORKDIR /app

# Copy environment file
COPY .env.example ./.env

# Expose both ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start both services using a process manager or background processes
CMD sh -c "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &"
