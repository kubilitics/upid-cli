# UPID CLI Docker Image
# Multi-stage build for optimized binary

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install PyInstaller
RUN pip install pyinstaller

# Set work directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy source code
COPY upid/ ./upid/
COPY setup.py .
COPY build/upid.spec .

# Build binary
RUN pyinstaller build/upid.spec --clean --noconfirm

# Runtime stage
FROM debian:bullseye-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r upid && useradd -r -g upid upid

# Set work directory
WORKDIR /app

# Copy binary from builder stage
COPY --from=builder /app/dist/upid /usr/local/bin/upid

# Make binary executable
RUN chmod +x /usr/local/bin/upid

# Create configuration directory
RUN mkdir -p /home/upid/.upid && \
    chown -R upid:upid /home/upid/.upid

# Switch to non-root user
USER upid

# Set environment variables
ENV PATH="/usr/local/bin:$PATH"
ENV HOME="/home/upid"

# Create default configuration
RUN mkdir -p /home/upid/.upid/logs && \
    cat > /home/upid/.upid/config.yaml << 'EOF'
# UPID CLI Configuration
version: 1.0.0

# Default settings
defaults:
  output_format: table
  local_mode: false
  dry_run: true

# Authentication settings
auth:
  auto_detect: true
  timeout: 30

# Logging settings
logging:
  level: info
  file: ~/.upid/logs/upid.log

# Performance settings
performance:
  max_workers: 4
  timeout: 60
EOF

# Set entrypoint
ENTRYPOINT ["upid"]

# Default command
CMD ["--help"] 