# Multi-stage Dockerfile for Analytics Service

# Stage 1: Build
FROM golang:1.21 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application with security flags
# NOTE: Kafka client requires CGO, so we set CGO_ENABLED=1
RUN CGO_ENABLED=1 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s -X main.version=$(git describe --tags --always --dirty)" \
    -o analytics-service ./cmd/analytics

# Stage 2: Runtime
FROM debian:bookworm-slim

# Install ca-certificates and necessary runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    tzdata \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

WORKDIR /app

# Copy the binary from builder
COPY --from=builder --chown=appuser:appuser /app/analytics-service .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:9090/metrics || exit 1

# Run the application
CMD ["./analytics-service"]
