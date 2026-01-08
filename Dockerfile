# Multi-stage build cho Vanna Agents
# Stage 1: Build web component
FROM node:20-alpine AS webcomponent-builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++

# Copy pyproject.toml first (needed by sync-version script)
COPY pyproject.toml ./

# Copy package files (for better caching)
COPY frontends/webcomponent/package.json ./frontends/webcomponent/
COPY frontends/webcomponent/package-lock.json* ./frontends/webcomponent/

# Change to webcomponent directory
WORKDIR /app/frontends/webcomponent

# Install dependencies
# Remove package-lock.json if exists to avoid sync issues, then install fresh
RUN rm -f package-lock.json && \
    npm install --legacy-peer-deps && \
    npm cache clean --force

# Copy all source files
COPY frontends/webcomponent/ ./

# Build web component
RUN npm run build

# Verify build output exists
RUN ls -la dist/ && \
    test -f dist/vanna-components.js || (echo "ERROR: Build failed - dist/vanna-components.js not found" && exit 1)

# Stage 2: Python server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    curl \
    apt-transport-https \
    ca-certificates \
    gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python project files
# README.md is required by pyproject.toml
COPY pyproject.toml ./
COPY setup.cfg ./
COPY README.md* ./
COPY src/ ./src/

# Install Python package and dependencies
# Split into separate RUN commands for better error handling
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

RUN pip install --no-cache-dir -e .

RUN pip install --no-cache-dir 'vanna[fastapi,gemini,mssql]' python-dotenv flask

# Copy built web component from stage 1
COPY --from=webcomponent-builder /app/frontends/webcomponent/dist ./frontends/webcomponent/dist

# Create directory for data
RUN mkdir -p /app/data

# Expose port
EXPOSE 3001

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Run server
CMD ["python", "-m", "vanna.servers", "--example", "gemini_mssql", "--port", "3001", "--host", "0.0.0.0", "--framework", "fastapi"]

