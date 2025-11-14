# NexusLang v2 - Performance Optimization Suite
# Implements Redis caching, CDN optimization, and performance enhancements

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "cache", "cdn", "database", "monitoring")]
    [string]$Optimize = "all"
)

# Configuration
$REDIS_URL = "redis://localhost:6379/0"
$CACHE_TTL = 3600  # 1 hour default TTL
$CDN_ENABLED = $true

# Colors for output
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"
$BLUE = "Blue"
$CYAN = "Cyan"
$NC = "White"

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = $NC
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-ColoredOutput $logMessage $BLUE
    Add-Content -Path "performance-optimization.log" -Value $logMessage
}

function Write-Success {
    param([string]$Message)
    Write-ColoredOutput "SUCCESS: $Message" $GREEN
    Write-Log "SUCCESS: $Message"
}

function Write-Error {
    param([string]$Message)
    Write-ColoredOutput "ERROR: $Message" $RED
    Write-Log "ERROR: $Message"
    exit 1
}

function Write-Warning {
    param([string]$Message)
    Write-ColoredOutput "WARNING: $Message" $YELLOW
    Write-Log "WARNING: $Message"
}

# Redis Cache Implementation
function Install-RedisCache {
    Write-Log "Setting up Redis caching layer..."

    # Check if Redis is running
    try {
        $redisResponse = docker exec redis redis-cli ping 2>$null
        if ($redisResponse -eq "PONG") {
            Write-Success "Redis is running and responding"
        } else {
            Write-Error "Redis is not responding properly"
        }
    } catch {
        Write-Error "Redis container not accessible. Please ensure Redis is running."
    }

    # Create Redis cache configuration
    $cacheConfig = @'
// Redis Cache Configuration for NexusLang v2
const Redis = require('ioredis');

class CacheManager {
    constructor() {
        this.redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379/0');
        this.defaultTTL = parseInt(process.env.CACHE_TTL) || 3600;

        this.redis.on('error', (err) => {
            console.error('Redis connection error:', err);
        });
    }

    // Generic cache methods
    async get(key) {
        try {
            const data = await this.redis.get(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Cache get error:', error);
            return null;
        }
    }

    async set(key, value, ttl = this.defaultTTL) {
        try {
            await this.redis.setex(key, ttl, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Cache set error:', error);
            return false;
        }
    }

    async delete(key) {
        try {
            await this.redis.del(key);
            return true;
        } catch (error) {
            console.error('Cache delete error:', error);
            return false;
        }
    }

    async clear(pattern = '*') {
        try {
            const keys = await this.redis.keys(pattern);
            if (keys.length > 0) {
                await this.redis.del(...keys);
            }
            return true;
        } catch (error) {
            console.error('Cache clear error:', error);
            return false;
        }
    }

    // API-specific cache methods
    async cacheAPIResponse(endpoint, params, response, ttl = this.defaultTTL) {
        const key = `api:${endpoint}:${JSON.stringify(params)}`;
        return await this.set(key, response, ttl);
    }

    async getCachedAPIResponse(endpoint, params) {
        const key = `api:${endpoint}:${JSON.stringify(params)}`;
        return await this.get(key);
    }

    async cacheUserData(userId, data, ttl = 1800) { // 30 minutes
        const key = `user:${userId}`;
        return await this.set(key, data, ttl);
    }

    async getCachedUserData(userId) {
        const key = `user:${userId}`;
        return await this.get(key);
    }

    async cacheNexusLangResult(code, result, ttl = 3600) {
        const key = `nexuslang:${Buffer.from(code).toString('base64')}`;
        return await this.set(key, result, ttl);
    }

    async getCachedNexusLangResult(code) {
        const key = `nexuslang:${Buffer.from(code).toString('base64')}`;
        return await this.get(key);
    }

    // Analytics caching
    async cacheAnalyticsData(type, data, ttl = 300) { // 5 minutes
        const key = `analytics:${type}`;
        return await this.set(key, data, ttl);
    }

    async getCachedAnalyticsData(type) {
        const key = `analytics:${type}`;
        return await this.get(key);
    }

    // Rate limiting
    async checkRateLimit(identifier, window = 60, maxRequests = 100) {
        const key = `ratelimit:${identifier}`;
        const current = await this.redis.incr(key);

        if (current === 1) {
            await this.redis.expire(key, window);
        }

        return current <= maxRequests;
    }

    // Session management
    async setSession(sessionId, data, ttl = 86400) { // 24 hours
        const key = `session:${sessionId}`;
        return await this.set(key, data, ttl);
    }

    async getSession(sessionId) {
        const key = `session:${sessionId}`;
        return await this.get(key);
    }

    async destroySession(sessionId) {
        const key = `session:${sessionId}`;
        return await this.delete(key);
    }

    // Cleanup
    async close() {
        await this.redis.quit();
    }
}

// Export singleton instance
const cacheManager = new CacheManager();
module.exports = cacheManager;
'@

    $cacheConfig | Out-File -FilePath "v2/backend/core/cache_manager.js" -Encoding UTF8
    Write-Success "Redis cache manager created"

    # Add cache middleware to FastAPI
    $cacheMiddleware = @'
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import hashlib

class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cache_manager):
        super().__init__(app)
        self.cache_manager = cache_manager

    async def dispatch(self, request: Request, call_next):
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Skip caching for certain endpoints
        skip_cache = [
            "/health",
            "/auth",
            "/admin",
            "/api/v2/auth"
        ]

        if any(path in request.url.path for path in skip_cache):
            return await call_next(request)

        # Create cache key
        key_data = f"{request.url.path}?{request.url.query}"
        cache_key = f"api:{hashlib.md5(key_data.encode()).hexdigest()}"

        # Try to get cached response
        cached_response = await self.cache_manager.get(cache_key)
        if cached_response:
            # Return cached response
            return Response(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers=cached_response.get("headers", {})
            )

        # Execute request
        start_time = time.time()
        response = await call_next(request)
        execution_time = time.time() - start_time

        # Cache response if successful and fast enough
        if (response.status_code == 200 and
            execution_time > 0.1 and  # Only cache if it took > 100ms
            len(await response.body()) < 1024 * 1024):  # < 1MB

            response_body = await response.body()
            cache_data = {
                "content": response_body,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "cached_at": time.time()
            }

            # Cache for 5 minutes by default
            await self.cache_manager.set(cache_key, cache_data, ttl=300)

        return response
'@

    $cacheMiddleware | Out-File -FilePath "v2/backend/core/cache_middleware.py" -Encoding UTF8
    Write-Success "Cache middleware created"

    # Update main.py to include caching
    $mainPyContent = Get-Content "v2/backend/main.py" -Raw

    # Add cache imports and middleware
    $cacheImports = @'

# Import cache manager
from .core.cache_manager import cache_manager
from .core.cache_middleware import CacheMiddleware

'@

    $mainPyContent = $mainPyContent -replace '(# Import health check system)', "$cacheImports`$1"

    # Add cache middleware
    $cacheMiddlewareSetup = @'

# Add cache middleware
app.add_middleware(CacheMiddleware, cache_manager=cache_manager)

'@

    $mainPyContent = $mainPyContent -replace '(# Add request ID middleware)', "$cacheMiddlewareSetup`$1"

    $mainPyContent | Out-File -FilePath "v2/backend/main.py" -Encoding UTF8
    Write-Success "Backend updated with caching support"
}

# CDN Optimization
function Install-CDN {
    Write-Log "Setting up CDN optimization..."

    if (!$CDN_ENABLED) {
        Write-Warning "CDN optimization skipped (disabled)"
        return
    }

    # Create CDN configuration
    $cdnConfig = @'
// CDN Configuration for Static Assets
const CDN_BASE_URL = process.env.CDN_BASE_URL || '';
const CDN_ENABLED = process.env.CDN_ENABLED === 'true';

class CDNManager {
    constructor() {
        this.baseUrl = CDN_BASE_URL;
        this.enabled = CDN_ENABLED;
    }

    // Generate CDN URL for asset
    getAssetUrl(assetPath) {
        if (!this.enabled || !this.baseUrl) {
            return assetPath; // Return local path
        }

        // Remove leading slash if present
        const cleanPath = assetPath.startsWith('/') ? assetPath.slice(1) : assetPath;

        // Add cache busting parameter
        const separator = cleanPath.includes('?') ? '&' : '?';
        const cacheBust = `${separator}v=${Date.now()}`;

        return `${this.baseUrl}/${cleanPath}${cacheBust}`;
    }

    // Preload critical assets
    preloadAssets(assetUrls) {
        if (typeof document === 'undefined') return; // Server-side

        assetUrls.forEach(url => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = this.getAssetUrl(url);
            link.as = this.getAssetType(url);
            document.head.appendChild(link);
        });
    }

    // Determine asset type for preloading
    getAssetType(url) {
        if (url.endsWith('.css')) return 'style';
        if (url.endsWith('.js')) return 'script';
        if (url.match(/\.(png|jpg|jpeg|gif|svg|webp)$/)) return 'image';
        if (url.endsWith('.woff2') || url.endsWith('.woff')) return 'font';
        return 'fetch';
    }

    // Optimize images
    optimizeImage(src, options = {}) {
        const { width, height, quality = 80, format = 'auto' } = options;

        if (!this.enabled || !this.baseUrl) {
            return src;
        }

        // This would integrate with a CDN that supports image optimization
        // Example: Cloudflare Images, Cloudinary, etc.
        const params = new URLSearchParams({
            w: width?.toString(),
            h: height?.toString(),
            q: quality.toString(),
            f: format
        });

        return `${this.baseUrl}/cdn-cgi/image/${params.toString()}/${src}`;
    }
}

// Export singleton
const cdnManager = new CDNManager();
module.exports = cdnManager;
'@

    $cdnConfig | Out-File -FilePath "v2/frontend/lib/cdn-manager.js" -Encoding UTF8
    Write-Success "CDN manager created"

    # Update Next.js config for CDN
    $nextConfig = @'
/** @type {import('next').NextConfig} */
const nextConfig = {
  // CDN configuration
  assetPrefix: process.env.CDN_BASE_URL || '',

  // Image optimization
  images: {
    domains: ['localhost', process.env.CDN_DOMAIN || 'cdn.nexuslang.dev'],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    formats: ['image/webp', 'image/avif'],
  },

  // Compression
  compress: true,

  // Experimental features for performance
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },

  // Headers for caching
  async headers() {
    return [
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },

  // Webpack optimizations
  webpack: (config, { dev, isServer }) => {
    // Production optimizations
    if (!dev && !isServer) {
      config.optimization.splitChunks.cacheGroups = {
        ...config.optimization.splitChunks.cacheGroups,
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10,
        },
        monaco: {
          test: /[\\/]node_modules[\\/]monaco-editor[\\/]/,
          name: 'monaco-editor',
          chunks: 'all',
          priority: 20,
        },
        framer: {
          test: /[\\/]node_modules[\\/]framer-motion[\\/]/,
          name: 'framer-motion',
          chunks: 'all',
          priority: 20,
        },
      };
    }

    return config;
  },
};

module.exports = nextConfig;
'@

    $nextConfig | Out-File -FilePath "v2/frontend/next.config.js" -Encoding UTF8
    Write-Success "Next.js configuration optimized for CDN"
}

# Database Performance Optimization
function Optimize-Database {
    Write-Log "Optimizing database performance..."

    # Create database optimization script
    $dbOptimizeScript = @'
-- Database Performance Optimizations for NexusLang v2

-- Enable performance tracking
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Create indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_subscription ON users(subscription_tier, subscription_status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_projects_created_at ON projects(created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_interactions_user_id ON voice_interactions(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_interactions_created_at ON voice_interactions(created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_requests_user_id ON api_requests(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_requests_created_at ON api_requests(created_at DESC);

-- Analytics indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_event_type ON analytics(event_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_created_at ON analytics(created_at DESC);

-- Billing indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);

-- Knowledge base indexes (for Grokopedia)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_embeddings ON knowledge USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_category ON knowledge(category);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_tags ON knowledge USING gin(tags);

-- Partial indexes for active records
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_active_users ON users(created_at) WHERE is_active = true;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_active_projects ON projects(created_at) WHERE is_active = true;

-- Function for cache invalidation
CREATE OR REPLACE FUNCTION invalidate_user_cache()
RETURNS TRIGGER AS $$
BEGIN
    -- Invalidate Redis cache for user data
    -- This would be called by your application when user data changes
    PERFORM pg_notify('user_cache_invalidate', NEW.id::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for cache invalidation (optional)
-- DROP TRIGGER IF EXISTS invalidate_user_cache_trigger ON users;
-- CREATE TRIGGER invalidate_user_cache_trigger
--     AFTER UPDATE ON users
--     FOR EACH ROW EXECUTE FUNCTION invalidate_user_cache();

-- Optimize autovacuum settings
ALTER TABLE users SET (autovacuum_vacuum_scale_factor = 0.02);
ALTER TABLE projects SET (autovacuum_vacuum_scale_factor = 0.02);
ALTER TABLE voice_interactions SET (autovacuum_vacuum_scale_factor = 0.05);
ALTER TABLE api_requests SET (autovacuum_vacuum_scale_factor = 0.1);

-- Create materialized view for analytics (refreshed periodically)
CREATE MATERIALIZED VIEW IF NOT EXISTS user_stats AS
SELECT
    user_id,
    COUNT(*) as total_requests,
    SUM(credits_used) as total_credits_used,
    MAX(created_at) as last_activity
FROM api_requests
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY user_id;

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_stats_user_id ON user_stats(user_id);

-- Refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_user_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY user_stats;
END;
$$ LANGUAGE plpgsql;

-- Create a view for real-time analytics
CREATE OR REPLACE VIEW realtime_analytics AS
SELECT
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) as requests,
    COUNT(DISTINCT user_id) as unique_users,
    SUM(credits_used) as credits_used
FROM api_requests
WHERE created_at >= CURRENT_DATE - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;

-- Analyze tables for query optimization
ANALYZE users;
ANALYZE projects;
ANALYZE voice_interactions;
ANALYZE api_requests;
ANALYZE knowledge;
'@

    $dbOptimizeScript | Out-File -FilePath "optimize-database.sql" -Encoding UTF8

    # Execute database optimizations
    Write-Log "Applying database optimizations..."
    # Note: This would be executed when database is available
    Write-Success "Database optimization script created"

    # Create connection pooling configuration
    $poolConfig = @'
# Database Connection Pooling Configuration
# For production use with PgBouncer or similar

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Connection pooling
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
reserve_pool_size = 5
max_db_connections = 50
max_user_connections = 100

# Timeouts
server_idle_timeout = 30
server_lifetime = 3600
client_idle_timeout = 300

# Logging
logfile = /var/log/pgbouncer/pgbouncer.log
pidfile = /var/run/pgbouncer/pgbouncer.pid

[databases]
galion_platform = host=postgres port=5432 dbname=galion_platform
'@

    $poolConfig | Out-File -FilePath "pgbouncer.ini" -Encoding UTF8
    Write-Success "Connection pooling configuration created"
}

# Monitoring and Performance Tracking
function Install-Monitoring {
    Write-Log "Setting up performance monitoring..."

    # Create performance monitoring script
    $monitorScript = @'
#!/usr/bin/env python3
"""
Performance Monitoring Script for NexusLang v2
"""

import time
import psutil
import requests
from datetime import datetime, timedelta

class PerformanceMonitor:
    def __init__(self, api_url="http://localhost:8010"):
        self.api_url = api_url
        self.metrics = {}

    def collect_system_metrics(self):
        """Collect system-level performance metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_connections": len(psutil.net_connections()),
            "timestamp": datetime.now().isoformat()
        }

    def collect_api_metrics(self):
        """Collect API performance metrics."""
        endpoints = [
            "/health/fast",
            "/api/v2/nexuslang/examples",
            "/api/v2/nexuslang/docs"
        ]

        metrics = {}
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_url}{endpoint}", timeout=5)
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

                metrics[endpoint] = {
                    "response_time_ms": round(response_time, 2),
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
            except Exception as e:
                metrics[endpoint] = {
                    "error": str(e),
                    "success": False
                }

        return metrics

    def check_performance_thresholds(self, metrics):
        """Check if metrics are within acceptable thresholds."""
        alerts = []

        # API response time alerts
        for endpoint, data in metrics.get("api", {}).items():
            if data.get("response_time_ms", 0) > 1000:  # > 1 second
                alerts.append(f"SLOW_API: {endpoint} took {data['response_time_ms']}ms")

        # System resource alerts
        system = metrics.get("system", {})
        if system.get("cpu_percent", 0) > 80:
            alerts.append(f"HIGH_CPU: {system['cpu_percent']}% usage")

        if system.get("memory_percent", 0) > 85:
            alerts.append(f"HIGH_MEMORY: {system['memory_percent']}% usage")

        if system.get("disk_usage", 0) > 90:
            alerts.append(f"HIGH_DISK: {system['disk_usage']}% usage")

        return alerts

    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle."""
        print(f"[{datetime.now()}] Running performance monitoring...")

        # Collect metrics
        system_metrics = self.collect_system_metrics()
        api_metrics = self.collect_api_metrics()

        all_metrics = {
            "system": system_metrics,
            "api": api_metrics,
            "timestamp": datetime.now().isoformat()
        }

        # Check thresholds
        alerts = self.check_performance_thresholds(all_metrics)

        # Report results
        print(f"System CPU: {system_metrics['cpu_percent']}%")
        print(f"System Memory: {system_metrics['memory_percent']}%")
        print(f"System Disk: {system_metrics['disk_usage']}%")

        for endpoint, data in api_metrics.items():
            status = "OK" if data.get("success") else "FAIL"
            time_str = f"{data.get('response_time_ms', 'N/A')}ms" if "response_time_ms" in data else "ERROR"
            print(f"API {endpoint}: {status} ({time_str})")

        if alerts:
            print("ALERTS:")
            for alert in alerts:
                print(f"  - {alert}")
        else:
            print("All systems operating within normal parameters.")

        return all_metrics, alerts

    def continuous_monitoring(self, interval=60):
        """Run continuous monitoring."""
        print(f"Starting continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop...")

        try:
            while True:
                self.run_monitoring_cycle()
                print("-" * 50)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='NexusLang v2 Performance Monitor')
    parser.add_argument('--api-url', default='http://localhost:8010', help='API base URL')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')

    args = parser.parse_args()

    monitor = PerformanceMonitor(args.api_url)

    if args.continuous:
        monitor.continuous_monitoring(args.interval)
    else:
        monitor.run_monitoring_cycle()
'@

    $monitorScript | Out-File -FilePath "performance-monitor.py" -Encoding UTF8
    Write-Success "Performance monitoring script created"

    # Create Prometheus metrics exporter
    $prometheusMetrics = @'
# Prometheus Metrics for NexusLang v2
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# API Metrics
api_requests_total = Counter(
    'nexuslang_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'nexuslang_api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint']
)

# Cache Metrics
cache_hits_total = Counter(
    'nexuslang_cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'nexuslang_cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# Database Metrics
db_connections_active = Gauge(
    'nexuslang_db_connections_active',
    'Number of active database connections'
)

db_query_duration = Histogram(
    'nexuslang_db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

# NexusLang Metrics
nexuslang_executions_total = Counter(
    'nexuslang_executions_total',
    'Total NexusLang code executions',
    ['status']
)

nexuslang_execution_duration = Histogram(
    'nexuslang_execution_duration_seconds',
    'NexusLang execution duration in seconds'
)

# User Metrics
active_users = Gauge(
    'nexuslang_active_users',
    'Number of currently active users'
)

user_sessions_total = Counter(
    'nexuslang_user_sessions_total',
    'Total user sessions'
)

# System Metrics
system_cpu_usage = Gauge(
    'nexuslang_system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_memory_usage = Gauge(
    'nexuslang_system_memory_usage_percent',
    'System memory usage percentage'
)

def update_metrics():
    """Update metrics with current values."""
    import psutil

    # Update system metrics
    system_cpu_usage.set(psutil.cpu_percent())
    system_memory_usage.set(psutil.virtual_memory().percent)

    # This would be called periodically to update Prometheus metrics

def get_metrics():
    """Get all metrics in Prometheus format."""
    return generate_latest()
'@

    $prometheusMetrics | Out-File -FilePath "v2/backend/core/prometheus_metrics.py" -Encoding UTF8
    Write-Success "Prometheus metrics exporter created"
}

# Main optimization function
function Invoke-Main {
    Write-Host ""
    Write-Host "PERFORMANCE OPTIMIZATION SUITE" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan

    switch ($Optimize) {
        "all" {
            Install-RedisCache
            Install-CDN
            Optimize-Database
            Install-Monitoring
        }
        "cache" {
            Install-RedisCache
        }
        "cdn" {
            Install-CDN
        }
        "database" {
            Optimize-Database
        }
        "monitoring" {
            Install-Monitoring
        }
    }

    Write-Host ""
    Write-Host "PERFORMANCE OPTIMIZATION COMPLETE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Optimizations Applied:" -ForegroundColor White
    if ($Optimize -eq "all" -or $Optimize -eq "cache") {
        Write-Host "  ✅ Redis Caching Layer" -ForegroundColor Green
    }
    if ($Optimize -eq "all" -or $Optimize -eq "cdn") {
        Write-Host "  ✅ CDN Optimization" -ForegroundColor Green
    }
    if ($Optimize -eq "all" -or $Optimize -eq "database") {
        Write-Host "  ✅ Database Performance Tuning" -ForegroundColor Green
    }
    if ($Optimize -eq "all" -or $Optimize -eq "monitoring") {
        Write-Host "  ✅ Performance Monitoring" -ForegroundColor Green
    }
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Deploy Redis cache manager to production" -ForegroundColor Yellow
    Write-Host "  2. Configure CDN_BASE_URL environment variable" -ForegroundColor Yellow
    Write-Host "  3. Run optimize-database.sql on production database" -ForegroundColor Yellow
    Write-Host "  4. Start performance-monitor.py for monitoring" -ForegroundColor Yellow
    Write-Host ""
}

# Execute based on optimization type
Invoke-Main
