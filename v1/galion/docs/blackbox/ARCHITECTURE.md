# Black Box Core - Architecture & Design

**Status:** Draft  
**Version:** 1.0.0  
**Date:** November 9, 2025  
**Philosophy:** First Principles Engineering

---

## Executive Summary

The **Black Box Core** is a sophisticated integration layer that connects Galion, Nexus services, AI capabilities, and external systems into a unified, intelligent platform. It serves as the central nervous system of the entire ecosystem.

**Key Responsibilities:**
1. **Service Orchestration** - Coordinate between 12+ microservices
2. **Event Processing** - Real-time event streaming and routing
3. **AI Integration** - Connect JARVIS AI to all system components
4. **Security Gateway** - Centralized authentication, authorization, and audit
5. **Monitoring & Observability** - System-wide telemetry and insights

---

## 1. Architecture Overview

### 1.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                      BLACK BOX CORE                         │
│                   (Integration Layer)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Event Bus  │  │ Orchestrator │  │ AI Gateway   │    │
│  │   (Kafka)    │  │  (Conductor) │  │  (JARVIS)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Auth Gateway │  │  Data Layer  │  │   Monitoring │    │
│  │   (Keycloak) │  │  (Postgres)  │  │ (Prometheus) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ↓                    ↓                    ↓
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │  Galion  │        │  Nexus   │        │ External │
    │ Services │        │ Services │        │ Systems  │
    └──────────┘        └──────────┘        └──────────┘
```

### 1.2 Core Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Event Bus** | Apache Kafka | Async message passing, event sourcing |
| **Orchestrator** | Netflix Conductor | Workflow orchestration, task scheduling |
| **AI Gateway** | Custom (Go/Python) | Route requests to JARVIS AI |
| **Auth Gateway** | Keycloak | SSO, OAuth2, OIDC, JWT management |
| **Data Layer** | PostgreSQL + Redis | Persistent storage, caching |
| **API Gateway** | Kong | Rate limiting, routing, load balancing |
| **Service Mesh** | Istio | mTLS, observability, traffic management |
| **Monitoring** | Prometheus + Grafana | Metrics, dashboards, alerting |

---

## 2. First Principles Analysis

### 2.1 Question Every Requirement

**Q:** Do we need a complex service mesh like Istio?  
**A:** YES (for production) - mTLS, observability, and traffic management are essential for 12+ services.

**Q:** Do we need Kafka for messaging?  
**A:** YES - Event sourcing, replay capability, and high throughput are critical.

**Q:** Do we need a separate orchestration engine?  
**A:** YES - Complex workflows (Galion) require visual management and retry logic.

**Q:** Do we need Keycloak for auth?  
**A:** MAYBE - Current JWT system works, but Keycloak provides SSO and better management.

### 2.2 Delete Unnecessary Parts

**DELETE:**
- ❌ Custom message queue (use Kafka, proven)
- ❌ Custom auth system (use Keycloak or current JWT)
- ❌ Custom monitoring (use Prometheus + Grafana)
- ❌ Multiple programming languages (standardize on Go/Python)
- ❌ Complex microservice decomposition (keep services cohesive)

**KEEP:**
- ✅ Event-driven architecture
- ✅ API Gateway pattern
- ✅ Centralized logging
- ✅ Service mesh (production only)

### 2.3 Simplify & Optimize

**Simplifications:**
1. **Single Event Bus** - Kafka for all async communication
2. **Single API Gateway** - Kong for all external traffic
3. **Single Auth Provider** - Keycloak or enhanced JWT
4. **Single Monitoring Stack** - Prometheus + Grafana + ELK
5. **Standardized Protocols** - gRPC internal, REST external

---

## 3. Event-Driven Architecture

### 3.1 Event Bus Design

```
┌─────────────────────────────────────────────────────────┐
│                    KAFKA CLUSTER                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Topics:                                                 │
│  ├── user.events (authentication, registration)         │
│  ├── task.events (creation, updates, completion)        │
│  ├── payment.events (transactions, invoices)            │
│  ├── voice.events (STT, TTS, commands)                  │
│  ├── ai.events (model inference, training)              │
│  ├── audit.events (security, compliance logs)           │
│  └── system.events (health, metrics, alerts)            │
│                                                          │
│  Partitions: 10 per topic (scalability)                 │
│  Replication: 3 (high availability)                     │
│  Retention: 7 days (compliance, debugging)              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Event Schema

```json
{
  "event_id": "uuid-v4",
  "event_type": "user.registered",
  "event_version": "1.0",
  "timestamp": "2025-11-09T12:00:00Z",
  "source_service": "auth-service",
  "correlation_id": "request-trace-id",
  "actor": {
    "user_id": 123,
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  },
  "payload": {
    "user_id": 123,
    "email": "user@example.com",
    "role": "member"
  },
  "metadata": {
    "region": "us-east-1",
    "environment": "production"
  }
}
```

### 3.3 Event Patterns

**Command Events** (Request-Response)
```
Service A → [command.do_something] → Service B
Service B → [result.something_done] → Service A
```

**Domain Events** (Broadcast)
```
Auth Service → [user.registered] → All Subscribers
  ↓
  ├── Email Service (send welcome email)
  ├── Analytics Service (track signup)
  └── Audit Service (log event)
```

**Saga Pattern** (Distributed Transactions)
```
Order Created → Reserve Inventory → Process Payment → Ship Order
     ↓ (fail)        ↓ (fail)           ↓ (fail)
Cancel Order ← Release Inventory ← Refund Payment ← Cancel Shipment
```

---

## 4. Service Orchestration

### 4.1 Workflow Engine (Netflix Conductor)

**Why Conductor?**
- ✅ Visual workflow designer
- ✅ Built-in retry and error handling
- ✅ Event-driven task execution
- ✅ Scalable (handles millions of workflows)
- ✅ Battle-tested at Netflix

### 4.2 Workflow Definition

```json
{
  "name": "user_onboarding",
  "version": 1,
  "tasks": [
    {
      "name": "send_verification_email",
      "taskReferenceName": "send_email",
      "type": "SIMPLE",
      "inputParameters": {
        "email": "${workflow.input.email}"
      }
    },
    {
      "name": "wait_for_verification",
      "taskReferenceName": "wait_verify",
      "type": "WAIT",
      "inputParameters": {
        "duration": "24h"
      }
    },
    {
      "name": "check_verification_status",
      "taskReferenceName": "check_status",
      "type": "DECISION",
      "caseValueParam": "verified",
      "decisionCases": {
        "true": [
          {
            "name": "activate_account",
            "taskReferenceName": "activate",
            "type": "SIMPLE"
          }
        ],
        "false": [
          {
            "name": "send_reminder",
            "taskReferenceName": "reminder",
            "type": "SIMPLE"
          }
        ]
      }
    }
  ]
}
```

### 4.3 Galion Workflow Integration

```nexuslang
// Define workflow in NexusLang
workflow OnboardDeveloper {
    description: "Onboard new developer to team"
    
    task("Send Contract") {
        assignee: role("HR")
        estimated_hours: 1
        
        on_complete: {
            trigger_workflow("SetupAccounts")
        }
    }
    
    task("Setup Accounts") {
        assignee: system
        parallel: [
            create_email_account(),
            create_github_account(),
            create_slack_account(),
            provision_aws_access()
        ]
    }
    
    task("Schedule Orientation") {
        assignee: role("Manager")
        depends_on: ["Setup Accounts"]
        
        on_complete: {
            notify(slack, "#team")
        }
    }
}
```

---

## 5. AI Gateway Integration

### 5.1 JARVIS AI Connection

```
User Request (Voice/Text)
    ↓
API Gateway (Authentication)
    ↓
Black Box AI Gateway
    ↓
    ├─→ Intent Recognition (NLP)
    ├─→ Context Retrieval (Vector DB)
    ├─→ Service Routing (Orchestrator)
    └─→ Response Generation (LLM)
    ↓
Format Response (JSON/Audio)
    ↓
Return to User
```

### 5.2 AI Gateway API

```go
// AI Gateway Service (Go)
package main

type AIGateway struct {
    jarvis      *JARVISClient
    conductor   *ConductorClient
    vectorDB    *QdrantClient
    cache       *RedisClient
}

func (g *AIGateway) ProcessRequest(ctx context.Context, req *AIRequest) (*AIResponse, error) {
    // 1. Parse input (voice → text if needed)
    text := req.Text
    if req.Audio != nil {
        text = g.jarvis.SpeechToText(req.Audio)
    }
    
    // 2. Understand intent
    intent := g.jarvis.ClassifyIntent(text)
    
    // 3. Retrieve relevant context
    context := g.vectorDB.Search(text, limit: 5)
    
    // 4. Route to appropriate service
    switch intent.Type {
    case "workflow.create":
        return g.createWorkflow(intent, context)
    case "user.query":
        return g.queryUser(intent, context)
    case "analytics.report":
        return g.generateReport(intent, context)
    default:
        return g.jarvis.GeneralResponse(text, context)
    }
}
```

### 5.3 Context Management

```python
# Context Manager (Python)
class ContextManager:
    def __init__(self):
        self.redis = RedisClient()
        self.postgres = PostgresClient()
        
    def get_conversation_context(self, user_id: int, session_id: str):
        """Retrieve last N messages + user preferences"""
        messages = self.redis.get(f"session:{session_id}:messages", limit=20)
        preferences = self.postgres.query(
            "SELECT * FROM user_preferences WHERE user_id = %s", 
            user_id
        )
        
        return {
            "messages": messages,
            "preferences": preferences,
            "timestamp": now()
        }
    
    def update_context(self, session_id: str, message: dict):
        """Store new message in context"""
        self.redis.rpush(f"session:{session_id}:messages", json.dumps(message))
        self.redis.expire(f"session:{session_id}:messages", 3600)  # 1 hour TTL
```

---

## 6. Security Architecture

### 6.1 Zero Trust Model

```
┌─────────────────────────────────────────────────┐
│           ZERO TRUST PRINCIPLES                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. Never Trust, Always Verify                 │
│     - Every request authenticated               │
│     - Continuous verification                   │
│                                                 │
│  2. Least Privilege Access                      │
│     - Minimal permissions granted               │
│     - Time-bound credentials                    │
│                                                 │
│  3. Assume Breach                               │
│     - Encrypt everything                        │
│     - Log all access                            │
│     - Segment networks                          │
│                                                 │
│  4. Verify Explicitly                           │
│     - Multi-factor authentication               │
│     - Device compliance checks                  │
│     - Location-based policies                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 6.2 Authentication Flow

```
1. User Login
   ↓
2. API Gateway (validate credentials)
   ↓
3. Auth Service (check 2FA)
   ↓
4. JWT Token Generated (15 min expiry)
   ↓
5. Refresh Token Stored (Redis, 7 days)
   ↓
6. Token Returned to Client
   ↓
7. Subsequent Requests (JWT in header)
   ↓
8. API Gateway (validate JWT)
   ↓
9. Service Mesh (mTLS between services)
   ↓
10. Target Service (process request)
```

### 6.3 Authorization Model (RBAC + ABAC)

```yaml
# Role-Based Access Control
roles:
  - admin:
      permissions: ["*"]
      
  - developer:
      permissions:
        - "task.create"
        - "task.update"
        - "task.view"
        - "user.view_self"
        
  - client:
      permissions:
        - "task.view"
        - "report.view"
        - "invoice.view"

# Attribute-Based Access Control
policies:
  - name: "owner_can_edit"
    effect: "allow"
    principal: "*"
    action: "task.update"
    resource: "task:*"
    condition:
      match:
        task.owner_id: "${user.id}"
        
  - name: "manager_can_view_team"
    effect: "allow"
    principal:
      role: "manager"
    action: "user.view"
    resource: "user:*"
    condition:
      match:
        user.team_id: "${principal.team_id}"
```

---

## 7. Data Management

### 7.1 Database Strategy

```
┌─────────────────────────────────────────────────┐
│              DATA ARCHITECTURE                  │
├─────────────────────────────────────────────────┤
│                                                 │
│  PostgreSQL (Primary Database)                  │
│  ├── Users, Authentication                      │
│  ├── Tasks, Workflows                           │
│  ├── Payments, Invoices                         │
│  └── Audit Logs                                 │
│                                                 │
│  Redis (Cache + Sessions)                       │
│  ├── Session storage (7 days TTL)              │
│  ├── Rate limiting counters                     │
│  ├── Temporary data (1 hour TTL)               │
│  └── Pub/Sub for real-time updates             │
│                                                 │
│  Kafka (Event Store)                            │
│  ├── Event sourcing (7 days retention)         │
│  ├── Replay capability                          │
│  └── Audit trail                                │
│                                                 │
│  S3 (Object Storage)                            │
│  ├── Documents, files                           │
│  ├── Voice recordings                           │
│  ├── Model weights                              │
│  └── Backups                                    │
│                                                 │
│  Qdrant (Vector Database)                       │
│  ├── AI embeddings                              │
│  ├── Semantic search                            │
│  └── RAG context                                │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 7.2 Data Flow

```
Write Operation:
  1. API Request → API Gateway
  2. Validation → Business Logic
  3. Write to PostgreSQL (transaction)
  4. Publish Event to Kafka
  5. Update Cache (Redis)
  6. Return Response

Read Operation:
  1. API Request → API Gateway
  2. Check Cache (Redis) - HIT → Return
  3. Cache MISS → Query PostgreSQL
  4. Store in Cache (Redis)
  5. Return Response

Event Processing:
  1. Event Published (Kafka)
  2. Consumers Subscribe
  3. Process Event (async)
  4. Update Databases
  5. Trigger Workflows (if needed)
```

---

## 8. Monitoring & Observability

### 8.1 Three Pillars

```
┌────────────────────────────────────────────┐
│         OBSERVABILITY STACK                │
├────────────────────────────────────────────┤
│                                            │
│  1. METRICS (Prometheus)                   │
│     - Request rate, latency, errors        │
│     - Resource usage (CPU, memory)         │
│     - Business metrics (signups, revenue)  │
│                                            │
│  2. LOGS (ELK Stack)                       │
│     - Application logs                     │
│     - Access logs                          │
│     - Audit logs                           │
│     - Error traces                         │
│                                            │
│  3. TRACES (Jaeger)                        │
│     - Distributed tracing                  │
│     - Request flow visualization           │
│     - Performance bottlenecks              │
│                                            │
└────────────────────────────────────────────┘
```

### 8.2 Grafana Dashboards

**System Overview Dashboard:**
- Service health (up/down)
- Request rate (requests/sec)
- Error rate (%)
- P50, P95, P99 latency
- Resource utilization

**Business Metrics Dashboard:**
- Active users (DAU/MAU)
- Tasks created/completed
- Revenue (hourly/daily)
- AI usage (voice requests)

**AI Performance Dashboard:**
- Model inference latency
- GPU utilization
- Voice quality metrics
- Accuracy scores

---

## 9. Deployment Architecture

### 9.1 Development Environment

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Black Box Services
  api-gateway:
    image: nexus/api-gateway:latest
    ports:
      - "8080:8080"
    depends_on:
      - redis
      - postgres
      
  orchestrator:
    image: conductor:latest
    ports:
      - "8081:8081"
    depends_on:
      - postgres
      - redis
      
  ai-gateway:
    image: nexus/ai-gateway:latest
    ports:
      - "9000:9000"
    environment:
      - JARVIS_API_URL=http://jarvis:8000
      
  # Existing Nexus Services
  auth-service:
    image: nexus/auth-service:latest
    
  user-service:
    image: nexus/user-service:latest
    
  # Infrastructure
  kafka:
    image: confluentinc/cp-kafka:7.5
    
  postgres:
    image: postgres:15
    
  redis:
    image: redis:7
    
  prometheus:
    image: prom/prometheus:latest
    
  grafana:
    image: grafana/grafana:latest
```

### 9.2 Production Environment (Kubernetes)

```yaml
# black-box-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-gateway
  namespace: nexus-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-gateway
  template:
    metadata:
      labels:
        app: ai-gateway
        version: v1
    spec:
      containers:
      - name: ai-gateway
        image: nexus/ai-gateway:v1.0.0
        ports:
        - containerPort: 9000
        env:
        - name: JARVIS_URL
          value: "http://jarvis-service:8000"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 9000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 9000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ai-gateway-service
spec:
  selector:
    app: ai-gateway
  ports:
  - port: 9000
    targetPort: 9000
  type: ClusterIP
```

---

## 10. API Specifications

### 10.1 Black Box REST API

```yaml
# OpenAPI 3.0 Specification
openapi: 3.0.0
info:
  title: Black Box Core API
  version: 1.0.0
  description: Integration layer for Nexus ecosystem

paths:
  /api/v1/orchestrate/workflow:
    post:
      summary: Start a workflow
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                workflow_name:
                  type: string
                input:
                  type: object
      responses:
        '200':
          description: Workflow started
          content:
            application/json:
              schema:
                type: object
                properties:
                  workflow_id:
                    type: string
                  status:
                    type: string
                    
  /api/v1/ai/query:
    post:
      summary: Query JARVIS AI
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                context:
                  type: object
      responses:
        '200':
          description: AI response
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                  confidence:
                    type: number
                    
  /api/v1/events/publish:
    post:
      summary: Publish event to bus
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                event_type:
                  type: string
                payload:
                  type: object
      responses:
        '202':
          description: Event accepted
```

---

## 11. Performance Targets

### 11.1 SLA Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Latency (P99)** | <100ms | Prometheus |
| **Event Processing** | <500ms | Kafka lag |
| **Workflow Execution** | <2s start | Conductor metrics |
| **AI Query Response** | <2s | Custom metrics |
| **Uptime** | 99.9% | Prometheus |
| **Error Rate** | <0.1% | Logs + metrics |

### 11.2 Scalability Targets

- **Concurrent Users:** 10,000
- **Events/Second:** 100,000
- **Workflows/Day:** 1,000,000
- **API Requests/Second:** 50,000

---

## 12. Cost Estimation

### 12.1 Infrastructure Costs (Monthly)

| Component | Cost |
|-----------|------|
| Kafka Cluster (3 nodes) | $300 |
| PostgreSQL (managed) | $200 |
| Redis (managed) | $100 |
| Kubernetes (EKS) | $150 |
| Load Balancers | $50 |
| Monitoring Stack | $100 |
| **Total** | **$900/month** |

### 12.2 Development Costs

| Phase | Duration | Cost |
|-------|----------|------|
| Architecture & Design | 4 weeks | $40K |
| Implementation | 16 weeks | $160K |
| Testing & QA | 4 weeks | $40K |
| **Total** | **24 weeks** | **$240K** |

---

## 13. Implementation Roadmap

### Week 1-4: Foundation
- ✅ Architecture design complete
- ✅ Technology selection finalized
- ✅ Development environment setup
- ✅ Initial prototypes

### Week 5-8: Core Services
- 🔄 Event bus implementation
- 🔄 API gateway enhancements
- 🔄 Orchestration engine setup
- 🔄 Basic monitoring

### Week 9-12: AI Integration
- ⏳ AI gateway development
- ⏳ JARVIS connection
- ⏳ Context management
- ⏳ Voice pipeline integration

### Week 13-16: Galion Integration
- ⏳ Workflow engine integration
- ⏳ Task management connection
- ⏳ Payment system hooks
- ⏳ Analytics pipeline

### Week 17-20: Security & Testing
- ⏳ Security hardening
- ⏳ Load testing
- ⏳ Penetration testing
- ⏳ Performance optimization

### Week 21-24: Production Deployment
- ⏳ Production infrastructure
- ⏳ Migration plan execution
- ⏳ Monitoring dashboards
- ⏳ Documentation

---

## 14. Success Metrics

### 14.1 Technical Metrics
- ✅ All services integrated
- ✅ <100ms P99 latency
- ✅ 99.9% uptime
- ✅ Zero data loss
- ✅ <0.1% error rate

### 14.2 Business Metrics
- ✅ 50% faster workflow execution
- ✅ 10x more events processed
- ✅ 90% reduction in manual operations
- ✅ Real-time AI responses

---

## Conclusion

The Black Box Core represents the foundation for a truly intelligent, integrated platform. By following first principles and leveraging proven technologies, we create a system that is:

- **Scalable:** Handle millions of events and requests
- **Reliable:** 99.9% uptime with automatic failover
- **Secure:** Zero-trust architecture with end-to-end encryption
- **Intelligent:** AI-powered automation and decision-making
- **Observable:** Complete visibility into system behavior

**Status:** Architecture Complete - Ready for Implementation

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Authors:** Project Nexus Team  
**License:** Proprietary




