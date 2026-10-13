# ==============================================================================
# QuestFlow // Production Multi-Stage Container Build
# ==============================================================================

# Stage 1: Frontend Static Assets & Node Server
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY questflow-frontend/package*.json ./
RUN npm install --omit=dev
COPY questflow-frontend/ .

# Stage 2: Backend Python ML & SDLC Microservice
FROM python:3.12-slim AS production
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies and install
COPY questflow-backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy application source code
COPY questflow-backend/ ./backend/
COPY --from=frontend-builder /app/frontend/ ./frontend/
COPY docs/ ./docs/
COPY tests/ ./tests/

# Environment configurations
ENV PORT=3000
ENV FLASK_PORT=5000
ENV PYTHONUNBUFFERED=1

EXPOSE 3000 5000

# Start script running both microservices
CMD ["sh", "-c", "python ./backend/app.py & node ./frontend/server.js"]
