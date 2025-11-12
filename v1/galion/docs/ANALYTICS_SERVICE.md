# 📊 Analytics Service

## Overview
The Analytics Service consumes events from Kafka, processes them in real-time, and stores them in PostgreSQL for analysis. It provides Prometheus metrics for monitoring system-wide activity.

**Technology:** Go 1.21, Kafka, PostgreSQL, Prometheus  
**Port:** 9090  
**Status:** Production Ready

## Core Responsibilities
- ✅ Real-time event processing from Kafka
- ✅ Event storage in PostgreSQL
- ✅ Prometheus metrics export
- ✅ Event deduplication
- ✅ Error handling and retry logic
- ✅ High-throughput processing (1000+ events/sec)

## Architecture

### Technology Stack
```
Language:     Go 1.21
Messaging:    Kafka 7.5
Database:     PostgreSQL 15
Monitoring:   Prometheus
```

### Event Flow
```
Services → Kafka (user-events topic) → Analytics Service → PostgreSQL
                                                         ↓
                                                    Prometheus Metrics
```

## Consumed Events

### Event Types
- `user_registered` - New user registration
- `user_login` - User login
- `profile_updated` - Profile changes
- `profile_viewed` - Profile views
- `user_search` - Search queries
- `user_activated` - Account activation
- `user_deactivated` - Account deactivation

### Event Schema
```json
{
  "event_type": "user_registered",
  "user_id": "uuid",
  "service": "auth-service",
  "timestamp": "2024-11-09T10:30:00Z",
  "data": {
    // Event-specific data
  }
}
```

## Database Storage

### Events Table
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id UUID NOT NULL,
    service VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_service ON events(service);
```

### Query Examples
```sql
-- Get all events for a user
SELECT * FROM events 
WHERE user_id = 'uuid' 
ORDER BY timestamp DESC;

-- Count events by type
SELECT event_type, COUNT(*) 
FROM events 
GROUP BY event_type;

-- Recent logins
SELECT * FROM events 
WHERE event_type = 'user_login' 
AND timestamp > NOW() - INTERVAL '24 hours';
```

## Prometheus Metrics

### Available Metrics
- `events_processed_total` - Total events processed (by type, service)
- `events_stored_total` - Total events in database
- `processing_errors_total` - Processing errors (by type, reason)
- `event_processing_duration_seconds` - Processing latency histogram
- `kafka_consumer_lag` - Consumer lag (events behind)

### Access Metrics
```bash
GET http://localhost:9090/metrics
```

## Configuration

### Environment Variables
```bash
# Metrics
METRICS_PORT=9090

# Kafka
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=user-events
KAFKA_GROUP_ID=analytics-service

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/nexuscore
```

## Monitoring

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "analytics-service"
}
```

## Performance

| Metric | Value |
|--------|-------|
| Event Throughput | 1000+ events/sec |
| Processing Latency | < 10ms per event |
| Consumer Lag | Typically 0 (real-time) |
| Memory Usage | ~50MB under normal load |

## Development

### Local Setup
```bash
cd services/analytics-service

# Install dependencies
go mod download

# Run service
go run cmd/analytics/main.go
```

## Grafana Integration
Pre-configured dashboards available at http://localhost:3000:
- Event Processing Overview
- User Activity Heatmap
- Service Health
- Event Type Distribution

---

**Last Updated:** November 9, 2024  
**Service Version:** 1.0.0  
**Status:** ✅ Production Ready

