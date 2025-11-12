# GALION Monitoring Guide
## Observability, Metrics, and Alerting

**Version:** 1.0  
**Date:** November 10, 2025  
**Purpose:** Complete guide to monitoring GALION infrastructure

---

## Monitoring Stack Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Architecture                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Exporters (Collect Metrics)                                │
│    ├─ Node Exporter (system metrics)                       │
│    ├─ cAdvisor (container metrics)                         │
│    ├─ Postgres Exporter (database metrics)                 │
│    ├─ Redis Exporter (cache metrics)                       │
│    └─ Nginx Exporter (web server metrics)                  │
│                                                             │
│  Prometheus (Store & Query Metrics)                         │
│    ├─ Scrapes metrics every 15s                            │
│    ├─ 30-day retention                                      │
│    └─ Evaluates alert rules                                │
│                                                             │
│  Grafana Cloud (Visualize & Alert)                          │
│    ├─ Dashboards                                            │
│    ├─ Alerts (email, Slack, PagerDuty)                     │
│    └─ Long-term storage (14 days free)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Cost:** $0 (Grafana Cloud free tier)

---

## Metrics Collection

### System Metrics (Node Exporter)

**Collected automatically from:**
- CPU usage per core
- Memory usage (total, free, cached)
- Disk I/O (read/write operations)
- Network I/O (bytes in/out)
- Load average (1min, 5min, 15min)
- Disk space per partition
- System uptime

**Access:** http://localhost:9100/metrics

**Key Metrics:**
```promql
# CPU usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100

# Network traffic
rate(node_network_receive_bytes_total[5m])
rate(node_network_transmit_bytes_total[5m])
```

### Container Metrics (cAdvisor)

**Collected automatically:**
- Per-container CPU usage
- Per-container memory usage
- Per-container network I/O
- Per-container disk I/O
- Container restart count

**Access:** http://localhost:8080/metrics

**Key Metrics:**
```promql
# Container memory usage
(container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100

# Container CPU usage
rate(container_cpu_usage_seconds_total[5m]) * 100

# Container restarts
rate(container_last_seen[5m]) > 0
```

### Database Metrics (Postgres Exporter)

**Collected automatically:**
- Active connections
- Transaction rate
- Query duration
- Cache hit ratio
- Database size
- Replication lag (if replicas exist)

**Access:** http://localhost:9187/metrics

**Key Metrics:**
```promql
# Connection count
pg_stat_database_numbackends

# Cache hit ratio
rate(pg_stat_database_blks_hit[5m]) / (rate(pg_stat_database_blks_hit[5m]) + rate(pg_stat_database_blks_read[5m]))

# Slow queries
pg_stat_statements_mean_time_seconds > 1

# Database size
pg_database_size_bytes
```

### Redis Metrics (Redis Exporter)

**Collected automatically:**
- Memory usage
- Connected clients
- Keyspace hits/misses
- Commands processed
- Evicted keys

**Access:** http://localhost:9121/metrics

**Key Metrics:**
```promql
# Cache hit rate
redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)

# Memory usage
(redis_memory_used_bytes / redis_memory_max_bytes) * 100

# Connected clients
redis_connected_clients
```

### Application Metrics

**Custom metrics to add to your FastAPI apps:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Request counter
request_counter = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Response time histogram
response_time = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Active users gauge
active_users = Gauge(
    'galion_active_users',
    'Number of active users'
)

# Business metrics
user_registrations = Counter(
    'galion_user_registrations_total',
    'Total user registrations'
)

voice_interactions = Counter(
    'galion_voice_interactions_total',
    'Total voice interactions',
    ['type']  # stt, tts, chat
)
```

**Expose metrics:**
```python
# In main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Auto-instrument FastAPI
Instrumentator().instrument(app).expose(app)

# Access at: http://localhost:8000/metrics
```

---

## Grafana Dashboards

### Dashboard 1: System Overview

**Panels:**

1. **CPU Usage (%)** - Line graph
   ```promql
   100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
   ```

2. **Memory Usage (%)** - Gauge
   ```promql
   (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
   ```

3. **Disk Usage (%)** - Gauge
   ```promql
   (1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100
   ```

4. **Network I/O** - Line graph
   ```promql
   rate(node_network_receive_bytes_total[5m])
   rate(node_network_transmit_bytes_total[5m])
   ```

5. **Load Average** - Line graph
   ```promql
   node_load1
   node_load5
   node_load15
   ```

### Dashboard 2: Application Performance

**Panels:**

1. **Request Rate (req/s)** - Line graph
   ```promql
   rate(http_requests_total[5m])
   ```

2. **Error Rate (%)** - Line graph
   ```promql
   (sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100
   ```

3. **Response Time Percentiles** - Line graph
   ```promql
   histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))  # P50
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))  # P95
   histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))  # P99
   ```

4. **Active Users** - Gauge
   ```promql
   galion_active_users
   ```

5. **Top Endpoints by Latency** - Table
   ```promql
   topk(10, sum by(endpoint) (rate(http_request_duration_seconds_sum[5m])) / sum by(endpoint) (rate(http_request_duration_seconds_count[5m])))
   ```

### Dashboard 3: Database Health

**Panels:**

1. **Connections** - Line graph
   ```promql
   pg_stat_database_numbackends
   ```

2. **Query Duration** - Line graph
   ```promql
   rate(pg_stat_statements_mean_time_seconds[5m])
   ```

3. **Cache Hit Ratio** - Gauge
   ```promql
   rate(pg_stat_database_blks_hit[5m]) / (rate(pg_stat_database_blks_hit[5m]) + rate(pg_stat_database_blks_read[5m]))
   ```

4. **Database Size** - Line graph
   ```promql
   pg_database_size_bytes
   ```

5. **Slow Queries Count** - Counter
   ```promql
   count(pg_stat_statements_mean_time_seconds > 1)
   ```

### Dashboard 4: Business Metrics

**Panels:**

1. **User Registrations (24h)** - Single stat
   ```promql
   increase(galion_user_registrations_total[24h])
   ```

2. **Active Users Trend** - Line graph
   ```promql
   galion_active_users
   ```

3. **Voice Interactions** - Line graph
   ```promql
   rate(galion_voice_interactions_total[5m])
   ```

4. **Revenue Metrics** (when implemented)
   ```promql
   galion_revenue_total
   galion_mrr
   ```

5. **User Retention** (when implemented)
   ```promql
   galion_dau / galion_mau
   ```

---

## Alerting Strategy

### Alert Severity Levels

**Critical (P0):** Page oncall immediately
- Site down
- Database down
- Data loss
- Security breach

**Warning (P1):** Slack notification
- High latency
- High error rate
- Resource constraints
- Performance degradation

**Info (P2):** Email only
- Scaling triggers
- Optimization opportunities
- Trend notifications

### Alert Configuration

Already configured in `monitoring/alerts.yml`.

**To enable alerts:**

1. Sign up for Grafana Cloud: https://grafana.com
2. Get Prometheus remote_write URL
3. Add to monitoring/prometheus.yml:
   ```yaml
   remote_write:
     - url: YOUR_GRAFANA_PROMETHEUS_URL
       basic_auth:
         username: YOUR_USERNAME
         password: YOUR_API_KEY
   ```
4. Restart Prometheus:
   ```bash
   docker compose restart prometheus
   ```

5. Configure alert channels in Grafana:
   - Email
   - Slack
   - PagerDuty

### Alert Examples

**High Memory Alert:**
```yaml
- alert: HighMemoryUsage
  expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
  for: 5m
  annotations:
    summary: "Server memory critically high"
    description: "Memory usage is {{ $value }}%"
```

**Custom Alert:**
```yaml
- alert: HighConcurrentUsers
  expr: galion_active_users > 500
  for: 15m
  labels:
    severity: info
  annotations:
    summary: "High traffic - consider scaling"
    description: "{{ $value }} concurrent users (threshold: 500)"
```

---

## Logging Strategy

### Log Levels

- **DEBUG:** Development only, verbose
- **INFO:** General information, request logs
- **WARNING:** Something unusual but handled
- **ERROR:** Error occurred, needs attention
- **CRITICAL:** System failure, immediate action

### Log Locations

**Application Logs:**
```bash
# Real-time
docker compose logs -f [service-name]

# Last 100 lines
docker compose logs --tail=100 [service-name]

# Since timestamp
docker compose logs --since 2025-11-10T10:00:00 [service-name]

# Specific log level
docker compose logs [service-name] | grep -i error
```

**System Logs:**
```bash
# System journal
sudo journalctl -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Auth logs (SSH attempts)
sudo tail -f /var/log/auth.log
```

### Log Aggregation (Future)

When you need centralized logging:

**Option 1: Loki + Promtail** (Free, self-hosted)
```yaml
# Add to docker-compose.yml
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"

promtail:
  image: grafana/promtail:latest
  volumes:
    - /var/log:/var/log:ro
```

**Option 2: Grafana Cloud Logs** (Free tier: 50GB)
- Sign up at grafana.com
- Install Grafana Agent
- Sends logs to Grafana Cloud

**Option 3: ELK Stack** (Elasticsearch, Logstash, Kibana)
- More powerful but complex
- Consider for >10K users

---

## Performance Monitoring

### Key Performance Indicators (KPIs)

**Availability:**
- Target: 99.9% uptime
- Measure: Uptime checks every 5 minutes
- Tool: UptimeRobot or Pingdom

**Latency:**
- Target: P99 < 500ms
- Measure: HTTP request duration
- Tool: Prometheus + Grafana

**Error Rate:**
- Target: <0.1%
- Measure: 5xx errors / total requests
- Tool: Prometheus + Grafana

**Throughput:**
- Target: Support 1000 concurrent users
- Measure: Requests per second
- Tool: Load testing (k6)

### Performance Baselines

Record baseline metrics for comparison:

**API Response Times (P95):**
- GET /health: ~50ms
- GET /api/v1/users/me: ~100ms
- POST /api/v1/conversations: ~200ms
- POST /api/v1/voice/chat: ~1500ms (includes external APIs)

**Database Query Times:**
- Simple SELECT: <10ms
- Complex JOIN: <50ms
- Aggregation: <100ms

**Cache Performance:**
- Redis hit rate: >80%
- Cache response time: <5ms

**Resource Usage (Idle):**
- CPU: 10-20%
- Memory: 40-50% (6-8GB of 16GB)
- Disk I/O: <10MB/s

**Resource Usage (Normal Load - 100 users):**
- CPU: 30-40%
- Memory: 60-70% (9-11GB)
- Disk I/O: <50MB/s

---

## Alerting Best Practices

### Alert Fatigue Prevention

**DO:**
- Set meaningful thresholds based on actual impact
- Use `for:` clause to avoid flapping (e.g., `for: 5m`)
- Group related alerts
- Use different channels for different severities

**DON'T:**
- Alert on every minor issue
- Set thresholds too low
- Send all alerts to same channel
- Alert without clear action

### Alert Tuning

Start conservative, tune based on experience:

```yaml
# Initial threshold (might be too sensitive)
- alert: HighCPU
  expr: cpu_usage > 70
  for: 5m

# After 1 week, if too many false positives:
- alert: HighCPU
  expr: cpu_usage > 80  # Increase threshold
  for: 10m              # Increase duration

# Or add more context:
- alert: HighCPU
  expr: cpu_usage > 70 AND error_rate > 0.01
  for: 5m
```

### Alert Routing

**Grafana Cloud:**
1. Configure contact points (email, Slack, etc.)
2. Create notification policies
3. Route by label:
   ```yaml
   severity: critical → PagerDuty (page oncall)
   severity: warning → Slack #alerts channel
   severity: info → Email only
   ```

---

## Dashboard Templates

### Import Pre-built Dashboards

Grafana has community dashboards for common exporters:

**Node Exporter Dashboard:**
- ID: 1860
- URL: https://grafana.com/grafana/dashboards/1860

**Docker Container Dashboard:**
- ID: 193
- URL: https://grafana.com/grafana/dashboards/193

**PostgreSQL Dashboard:**
- ID: 9628
- URL: https://grafana.com/grafana/dashboards/9628

**Redis Dashboard:**
- ID: 11835
- URL: https://grafana.com/grafana/dashboards/11835

**Import in Grafana:**
1. Go to Dashboards → Import
2. Enter dashboard ID
3. Select Prometheus data source
4. Click Import

---

## Querying Prometheus

### PromQL Examples

**Find services that are down:**
```promql
up == 0
```

**Calculate request rate:**
```promql
rate(http_requests_total[5m])
```

**Calculate error rate:**
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

**Find top endpoints by latency:**
```promql
topk(10, sum by(endpoint) (rate(http_request_duration_seconds_sum[5m])) / sum by(endpoint) (rate(http_request_duration_seconds_count[5m])))
```

**Memory usage over time:**
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

**Database connection count:**
```promql
sum(pg_stat_database_numbackends) by (datname)
```

### PromQL Tips

**Aggregation operators:**
- `sum()` - Add values
- `avg()` - Average
- `min()` / `max()` - Min/max
- `count()` - Count number of series
- `topk(N, metric)` - Top N values
- `bottomk(N, metric)` - Bottom N values

**Rate functions:**
- `rate()` - Per-second average over time range
- `irate()` - Instant rate (last 2 samples)
- `increase()` - Total increase over time range

**Filtering:**
```promql
# By label
metric_name{job="app-api"}

# By regex
metric_name{status=~"5.."}

# Multiple labels
metric_name{job="app-api", status="200"}
```

---

## Monitoring Checklist

### Setup Checklist
- [x] Prometheus running and scraping metrics
- [x] All exporters running
- [x] Grafana Cloud configured (optional)
- [x] Alert rules loaded
- [x] Alert channels configured
- [x] Dashboards created
- [ ] Uptime monitoring (UptimeRobot)
- [ ] Log aggregation (Loki)

### Daily Monitoring
- [ ] Check Grafana for active alerts
- [ ] Review error rate (should be <0.1%)
- [ ] Check response time trends
- [ ] Verify backups completed
- [ ] Review resource usage

### Weekly Review
- [ ] Analyze performance trends
- [ ] Review slow query logs
- [ ] Check cache hit rates
- [ ] Review security logs
- [ ] Update alert thresholds if needed

### Monthly Review
- [ ] Review dashboards for insights
- [ ] Optimize based on patterns
- [ ] Plan capacity (scaling needs)
- [ ] Update SLOs if needed
- [ ] Archive old metrics

---

## Service Level Objectives (SLOs)

### Target SLOs

**Availability:** 99.9% uptime
- Allows: 43 minutes downtime per month
- Measure: Uptime checks
- Alert: If downtime >5 minutes

**Latency:** P95 < 500ms, P99 < 1s
- Measure: HTTP request duration
- Alert: If P99 >1s for 5 minutes

**Error Rate:** <0.1% of requests
- Measure: 5xx errors / total requests
- Alert: If error rate >1% for 5 minutes

**Throughput:** Support 500 concurrent users
- Measure: Active connections
- Alert: If >500 users (scaling trigger)

### SLO Tracking

**Calculate SLO compliance:**
```promql
# Availability over 30 days
(sum(up) / count(up)) * 100

# Latency P95 compliance
(count(http_request_duration_seconds < 0.5) / count(http_request_duration_seconds)) * 100

# Error rate compliance
(1 - (sum(http_requests_total{status=~"5.."}) / sum(http_requests_total))) * 100
```

---

## Custom Metrics to Add

### User Engagement Metrics

```python
from prometheus_client import Counter, Gauge

# Track daily active users
daily_active_users = Gauge('galion_dau', 'Daily active users')

# Track feature usage
feature_usage = Counter('galion_feature_usage', 'Feature usage count', ['feature_name'])

# Track voice interaction quality
voice_quality_score = Histogram('galion_voice_quality', 'Voice interaction quality score', buckets=[1,2,3,4,5])
```

### Business Metrics

```python
# Revenue tracking
monthly_recurring_revenue = Gauge('galion_mrr', 'Monthly recurring revenue')

# Churn rate
churn_rate = Gauge('galion_churn_rate', 'Monthly churn rate')

# Customer lifetime value
customer_ltv = Gauge('galion_customer_ltv', 'Average customer lifetime value')
```

### Infrastructure Metrics

```python
# Deployment frequency
deployments_total = Counter('galion_deployments_total', 'Total deployments')

# Backup success rate
backup_success = Counter('galion_backup_success', 'Successful backups')
backup_failure = Counter('galion_backup_failure', 'Failed backups')

# Certificate expiry
cert_expiry_days = Gauge('galion_cert_expiry_days', 'Days until certificate expiry')
```

---

## Integration with External Tools

### UptimeRobot (Free Tier)

Setup external uptime monitoring:

1. Sign up: https://uptimerobot.com
2. Add monitors:
   - galion.app
   - api.galion.app
   - studio.galion.app
   - api.studio.galion.app
3. Check interval: 5 minutes
4. Alert: Email + Slack

### Sentry (Error Tracking)

For detailed error tracking:

```python
# Install: pip install sentry-sdk

# In main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of requests
    environment="production"
)
```

Cost: Free tier includes 5K errors/month

---

## Troubleshooting Monitoring

### Prometheus not scraping

**Check targets:**
```bash
# Via API
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Via UI
# Go to http://localhost:9090/targets
```

**Common issues:**
- Service not exposing /metrics endpoint
- Network connectivity issues
- Wrong port in prometheus.yml

### Grafana not showing data

**Check:**
1. Prometheus data source configured?
2. Correct Prometheus URL?
3. Queries working in Prometheus?
4. Time range correct in Grafana?

### Alerts not firing

**Check:**
1. Alert rules loaded in Prometheus?
   ```bash
   curl http://localhost:9090/api/v1/rules
   ```

2. Alert condition actually met?
   - Test query in Prometheus
   - Check `for:` duration

3. Alert channels configured in Grafana?

---

**Remember:** Good monitoring is proactive, not reactive.  
**Watch trends, not just current values.**  
**Alert on impact, not just symptoms.**

---

**Version:** 1.0  
**Last Updated:** November 10, 2025  
**Next Review:** Monthly

