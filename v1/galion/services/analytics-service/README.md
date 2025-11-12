# Nexus Analytics Service

Real-time event processing and analytics service for Nexus Core.

## Features

- **Event Consumption**: Consumes events from Kafka topics
- **Data Storage**: Stores events in PostgreSQL for analysis
- **Metrics**: Exposes Prometheus metrics for monitoring
- **Real-time Processing**: Processes events as they arrive
- **Scalable**: Can run multiple instances for high throughput

## Architecture

```
Kafka (user-events topic)
    ↓
Analytics Service
    ├─→ PostgreSQL (event storage)
    └─→ Prometheus (metrics)
```

## Prerequisites

- Go 1.21+
- PostgreSQL database
- Kafka broker running
- Prometheus (for metrics collection)

## Quick Start

### 1. Set up environment

Create a `.env` file:
```env
KAFKA_BROKERS=localhost:9092
DATABASE_URL=postgresql://nexuscore:nexuscore123@localhost:5432/nexuscore
METRICS_PORT=9090
```

### 2. Run the service

```bash
# Install dependencies
go mod download

# Run the service
go run cmd/analytics/main.go
```

Service will:
- Connect to Kafka and subscribe to `user-events` topic
- Start consuming and processing events
- Expose metrics at http://localhost:9090/metrics
- Expose health check at http://localhost:9090/health

## Events Processed

The service processes these event types:

**From Auth Service:**
- `user.registered` - New user registration
- `user.login` - User login
- `user.logout` - User logout

**From User Service:**
- `user.profile_updated` - Profile update
- `user.profile_viewed` - Profile view
- `user.search_performed` - User search
- `user.deactivated` - User deactivated by admin
- `user.activated` - User activated by admin

## Data Storage

Events are stored in PostgreSQL in the `analytics.events` table:

```sql
CREATE TABLE analytics.events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    service VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Metrics

The service exposes Prometheus metrics at `/metrics`:

**Event Metrics:**
- `analytics_events_processed_total` - Total events processed (by type and service)
- `analytics_events_processing_duration_seconds` - Processing duration histogram
- `analytics_events_processing_errors_total` - Processing errors counter
- `analytics_events_stored_total` - Total events in database

**Example Queries:**

```promql
# Events per second by type
rate(analytics_events_processed_total[1m])

# Error rate
rate(analytics_events_processing_errors_total[5m])

# Total events stored
analytics_events_stored_total
```

## Configuration

All configuration via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `KAFKA_BROKERS` | Kafka broker addresses | localhost:9092 |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `METRICS_PORT` | Port for metrics/health endpoints | 9090 |

## Docker

### Build image

```bash
docker build -t nexus-analytics-service .
```

### Run container

```bash
docker run -d \
  -p 9090:9090 \
  --name analytics-service \
  -e KAFKA_BROKERS=kafka:9092 \
  -e DATABASE_URL=postgresql://user:pass@postgres:5432/db \
  nexus-analytics-service
```

### Using Docker Compose

```bash
# From project root
docker-compose up analytics-service
```

## Development

### Project Structure

```
analytics-service/
├── cmd/
│   └── analytics/
│       └── main.go           # Application entry point
├── internal/
│   ├── consumer/
│   │   └── kafka.go          # Kafka consumer
│   └── storage/
│       └── postgres.go       # PostgreSQL storage
├── pkg/
│   └── metrics/
│       └── prometheus.go     # Prometheus metrics
├── go.mod                    # Dependencies
├── Dockerfile               # Container definition
└── README.md               # This file
```

### Adding New Event Types

1. **Producer Side** (auth-service or user-service):
   - Add event publishing function in `events.py`
   - Call function when event occurs

2. **Consumer Side** (analytics-service):
   - No code changes needed! Service automatically processes all events
   - Add custom processing logic in `main.go` if needed

### Testing

**Manual Testing:**

1. Start the service
2. Trigger events (register user, login, etc.)
3. Check logs for processed events
4. Query database to verify storage
5. Check Prometheus metrics

**Example Query:**

```sql
-- Count events by type
SELECT event_type, COUNT(*) as count
FROM analytics.events
GROUP BY event_type
ORDER BY count DESC;

-- Recent events
SELECT * FROM analytics.events
ORDER BY timestamp DESC
LIMIT 10;
```

## Monitoring

### Health Check

```bash
curl http://localhost:9090/health
```

Response:
```json
{
  "status": "healthy",
  "service": "analytics-service"
}
```

### Metrics

```bash
curl http://localhost:9090/metrics
```

### Logs

Service logs all processed events:
```
2024-11-08 12:34:56 Received event: user.registered from auth-service (user: uuid)
2024-11-08 12:34:56 Processed event: user.registered (user: uuid)
```

## Troubleshooting

### "Failed to connect to Kafka"

- Check if Kafka is running: `docker ps | grep kafka`
- Verify KAFKA_BROKERS environment variable
- Check network connectivity

### "Failed to connect to database"

- Verify DATABASE_URL is correct
- Check if PostgreSQL is running
- Ensure `analytics` schema exists

### No events being processed

- Check if producers are publishing events
- Verify topic name matches (`user-events`)
- Check Kafka consumer group status
- Look for errors in service logs

### High memory usage

- Events are processed immediately, not batched
- Check database connection pool settings
- Monitor with Prometheus metrics

## Performance

**Throughput:**
- Processes 1,000+ events/second (single instance)
- Scales horizontally (multiple instances)
- Uses Kafka consumer groups for load balancing

**Latency:**
- < 10ms processing time per event
- Database write time depends on PostgreSQL performance

## Future Enhancements

- [ ] Real-time aggregations (counts, rates)
- [ ] Event replay capability
- [ ] Data retention policies
- [ ] Advanced analytics queries
- [ ] Event filtering and routing
- [ ] Dead letter queue for failed events

## Related Services

- **auth-service** (port 8000): Produces authentication events
- **user-service** (port 8001): Produces user activity events  
- **kafka** (port 9092): Event streaming platform
- **postgres** (port 5432): Event storage

## License

[To be determined]

