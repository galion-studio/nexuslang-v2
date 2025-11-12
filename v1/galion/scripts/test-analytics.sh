#!/bin/bash
# Test script for Analytics Service integration
# Tests complete event flow: register user → check Kafka → verify analytics processes → check database

set -e

echo "=========================================="
echo "Testing Analytics Service Integration"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking if services are running...${NC}"
if ! docker ps | grep -q "nexus-postgres\|nexus-kafka\|nexus-analytics-service"; then
    echo -e "${YELLOW}Services not running. Starting services...${NC}"
    docker-compose up -d postgres redis zookeeper kafka analytics-service
    echo "Waiting for services to be ready..."
    sleep 15
else
    echo -e "${GREEN}Services are running${NC}"
fi

echo ""
echo -e "${YELLOW}Step 2: Registering a test user...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analytics-test@example.com",
    "password": "TestPassword123!",
    "name": "Analytics Test User"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}User registered successfully${NC}"
    USER_ID=$(echo "$REGISTER_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    echo "User ID: $USER_ID"
else
    echo -e "${RED}Failed to register user${NC}"
    echo "Response: $REGISTER_RESPONSE"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 3: Waiting for event to be processed (5 seconds)...${NC}"
sleep 5

echo ""
echo -e "${YELLOW}Step 4: Checking analytics service logs for processed events...${NC}"
ANALYTICS_LOGS=$(docker logs nexus-analytics-service --tail 50 2>&1)
if echo "$ANALYTICS_LOGS" | grep -q "user.registered"; then
    echo -e "${GREEN}✓ Event found in analytics service logs${NC}"
    echo "$ANALYTICS_LOGS" | grep "user.registered" | tail -1
else
    echo -e "${RED}✗ Event not found in analytics service logs${NC}"
    echo "Recent logs:"
    echo "$ANALYTICS_LOGS" | tail -10
fi

echo ""
echo -e "${YELLOW}Step 5: Checking database for stored events...${NC}"
DB_RESULT=$(docker exec -i nexus-postgres psql -U nexuscore -d nexuscore -t -c \
  "SELECT COUNT(*) FROM analytics.events WHERE event_type = 'user.registered';" 2>&1)

if [ $? -eq 0 ]; then
    EVENT_COUNT=$(echo "$DB_RESULT" | tr -d ' \n')
    if [ "$EVENT_COUNT" -gt "0" ]; then
        echo -e "${GREEN}✓ Found $EVENT_COUNT event(s) in database${NC}"
        
        # Show recent events
        echo ""
        echo "Recent events:"
        docker exec -i nexus-postgres psql -U nexuscore -d nexuscore -c \
          "SELECT event_type, user_id, service, timestamp FROM analytics.events ORDER BY timestamp DESC LIMIT 5;"
    else
        echo -e "${RED}✗ No events found in database${NC}"
    fi
else
    echo -e "${RED}✗ Failed to query database${NC}"
    echo "Error: $DB_RESULT"
fi

echo ""
echo -e "${YELLOW}Step 6: Checking Prometheus metrics...${NC}"
METRICS=$(curl -s http://localhost:9090/metrics)
if echo "$METRICS" | grep -q "analytics_events_processed_total"; then
    echo -e "${GREEN}✓ Prometheus metrics are available${NC}"
    echo "$METRICS" | grep "analytics_events_processed_total" | head -5
else
    echo -e "${RED}✗ Prometheus metrics not found${NC}"
fi

echo ""
echo -e "${YELLOW}Step 7: Testing login event...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8080/api/v1/auth/login?email=analytics-test@example.com&password=TestPassword123!")
if echo "$LOGIN_RESPONSE" | grep -q "token"; then
    echo -e "${GREEN}Login successful${NC}"
    sleep 3
    
    # Check for login event
    LOGIN_EVENTS=$(docker exec -i nexus-postgres psql -U nexuscore -d nexuscore -t -c \
      "SELECT COUNT(*) FROM analytics.events WHERE event_type = 'user.login';" 2>&1)
    if [ $? -eq 0 ]; then
        LOGIN_COUNT=$(echo "$LOGIN_EVENTS" | tr -d ' \n')
        if [ "$LOGIN_COUNT" -gt "0" ]; then
            echo -e "${GREEN}✓ Login event found in database${NC}"
        else
            echo -e "${YELLOW}⚠ Login event not yet in database (may take a few seconds)${NC}"
        fi
    fi
else
    echo -e "${RED}Login failed${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Test Complete!${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "- User registration: ✓"
echo "- Event publishing: Check logs above"
echo "- Analytics processing: Check logs above"
echo "- Database storage: Check database query above"
echo "- Prometheus metrics: Check metrics above"
echo ""
echo "To view analytics service logs:"
echo "  docker logs nexus-analytics-service -f"
echo ""
echo "To query events in database:"
echo "  docker exec -it nexus-postgres psql -U nexuscore -d nexuscore"
echo "  SELECT * FROM analytics.events ORDER BY timestamp DESC LIMIT 10;"

