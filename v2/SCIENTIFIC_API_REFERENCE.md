# Nexus Lang V2 Scientific API Reference

## Overview

The Nexus Lang V2 Scientific API provides comprehensive access to advanced scientific knowledge processing capabilities, including first principles reasoning, multi-agent collaboration, and external knowledge integration.

## Authentication

All API endpoints require authentication via JWT token:

```bash
Authorization: Bearer <your_jwt_token>
```

## Scientific Knowledge Endpoints

### POST `/api/v1/grokopedia/scientific-query`

Execute comprehensive scientific queries using specialized science agents.

#### Request Body

```typescript
interface ScientificQueryRequest {
  query: string;                    // Scientific question or problem
  domain_focus?: "physics" | "chemistry" | "mathematics" | "multi" | null;
  require_collaboration?: boolean;  // Default: true
  include_external_sources?: boolean; // Default: true
  first_principles_only?: boolean;  // Default: false
  context?: Record<string, any>;    // Additional context
}
```

#### Response Body

```typescript
interface ScientificQueryResponse {
  query: string;
  domain: string;
  analysis_result: ScientificAnalysisResult;
  external_knowledge?: ExternalKnowledgeResult;
  confidence_score: number;         // 0.0 to 1.0
  processing_time: number;          // seconds
  sources_used: string[];           // List of sources consulted
  first_principles_applied: string[]; // First principles used
  transparency_report: TransparencyReport;
}

interface ScientificAnalysisResult {
  scientific_method: "first_principles" | "empirical" | "theoretical";
  fundamental_principles: string[];
  cross_domain_connections: CrossDomainConnection[];
  agent_contributions: Record<string, AgentContribution>;
  validation_results: ValidationResult[];
  predictions?: ScientificPrediction[];
}

interface CrossDomainConnection {
  domains: string[];
  connection: string;
  example: string;
  strength: number;  // 0.0 to 1.0
}

interface AgentContribution {
  agent_name: string;
  contribution_type: "analysis" | "validation" | "synthesis";
  confidence: number;
  key_insights: string[];
  limitations: string[];
}

interface ValidationResult {
  claim: string;
  validation_method: "first_principles" | "empirical" | "logical";
  result: "supported" | "refuted" | "inconclusive";
  evidence_strength: "strong" | "moderate" | "weak";
  counter_evidence?: string[];
}
```

#### Example Usage

```python
import requests

# Single-domain physics query
response = requests.post("/api/v1/grokopedia/scientific-query", json={
    "query": "Explain the photoelectric effect using first principles",
    "domain_focus": "physics",
    "require_collaboration": False,
    "include_external_sources": True
})

result = response.json()
print(f"Confidence: {result['confidence_score']}")
print(f"Domain: {result['domain']}")
```

---

### POST `/api/v1/grokopedia/first-principles-analysis`

Perform detailed first principles analysis of scientific topics following Elon Musk's methodology.

#### Request Body

```typescript
interface FirstPrinciplesAnalysisRequest {
  topic: string;
  domain: "physics" | "chemistry" | "mathematics";
  depth: "basic" | "comprehensive" | "exhaustive";  // Default: "comprehensive"
  include_counterexamples: boolean;  // Default: true
  context?: Record<string, any>;
}
```

#### Response Body

```typescript
interface FirstPrinciplesAnalysisResponse {
  topic: string;
  domain: string;
  fundamental_principles: string[];
  logical_deduction_steps: DeductionStep[];
  counterexamples: Counterexample[];
  conclusions: Conclusion[];
  confidence_level: "high" | "moderate" | "low";
  validation_methods: string[];
  processing_metadata: ProcessingMetadata;
}

interface DeductionStep {
  step_number: number;
  description: string;
  starting_assumptions: string[];
  logical_operation: string;
  result: string;
  confidence: number;
}

interface Counterexample {
  scenario: string;
  why_invalid: string;
  lesson_learned: string;
}

interface Conclusion {
  statement: string;
  evidence_strength: "strong" | "moderate" | "weak";
  limitations: string[];
  further_investigation: string[];
}
```

#### Example Usage

```python
# First principles analysis of thermodynamics
response = requests.post("/api/v1/grokopedia/first-principles-analysis", json={
    "topic": "thermodynamics",
    "domain": "physics",
    "depth": "comprehensive",
    "include_counterexamples": True
})

analysis = response.json()
for principle in analysis['fundamental_principles']:
    print(f"Fundamental: {principle}")
```

---

### POST `/api/v1/grokopedia/scientific-validation`

Validate scientific claims using evidence-based reasoning and multiple validation methods.

#### Request Body

```typescript
interface ScientificValidationRequest {
  claim: string;
  domain: "physics" | "chemistry" | "mathematics" | "general";
  evidence_types: ("experimental" | "theoretical" | "observational" | "empirical")[];
  validation_depth: "basic" | "comprehensive" | "exhaustive";  // Default: "comprehensive"
  include_alternatives: boolean;  // Default: true
}
```

#### Response Body

```typescript
interface ScientificValidationResponse {
  claim: string;
  domain: string;
  validation_result: "supported" | "refuted" | "inconclusive";
  evidence_strength: "strong" | "moderate" | "weak";
  confidence_score: number;  // 0.0 to 1.0
  validation_methods_used: ValidationMethod[];
  evidence_found: Evidence[];
  counter_evidence: Evidence[];
  alternative_explanations: AlternativeExplanation[];
  recommended_actions: string[];
  validation_metadata: ValidationMetadata;
}

interface ValidationMethod {
  method: string;
  effectiveness: number;  // 0.0 to 1.0
  evidence_quality: "high" | "medium" | "low";
  limitations: string[];
}

interface Evidence {
  type: "experimental" | "theoretical" | "observational";
  description: string;
  source: string;
  reliability: number;  // 0.0 to 1.0
  date?: string;
}

interface AlternativeExplanation {
  explanation: string;
  probability: number;  // 0.0 to 1.0
  supporting_evidence: string[];
  why_not_primary: string;
}
```

#### Example Usage

```python
# Validate a physics claim
response = requests.post("/api/v1/grokopedia/scientific-validation", json={
    "claim": "Energy cannot be created or destroyed",
    "domain": "physics",
    "evidence_types": ["experimental", "theoretical", "observational"]
})

validation = response.json()
print(f"Result: {validation['validation_result']}")
print(f"Confidence: {validation['confidence_score']}")
```

---

## Transparency Endpoints

### GET `/api/v1/transparency/report/{execution_id}`

Retrieve detailed transparency report for a specific execution.

#### Path Parameters

- `execution_id`: Unique identifier for the execution

#### Response Body

```typescript
interface TransparencyReportResponse {
  execution_id: string;
  summary: ExecutionSummary;
  reasoning_steps: ReasoningStep[];
  knowledge_sources: KnowledgeSource[];
  validation_records: ValidationRecord[];
  audit_trail: string[];
}

interface ExecutionSummary {
  query: string;
  agent: string;
  duration: number;  // seconds
  final_confidence: number;
  transparency_score: number;
  steps_count: number;
  sources_count: number;
  validations_count: number;
  start_time: string;
  end_time: string;
}
```

#### Example Usage

```python
# Get transparency report
response = requests.get(f"/api/v1/transparency/report/sci_12345")
report = response.json()

print(f"Execution: {report['execution_id']}")
print(f"Transparency Score: {report['summary']['transparency_score']}")
print(f"Duration: {report['summary']['duration']}s")
```

---

### GET `/api/v1/transparency/statistics`

Get comprehensive transparency system statistics.

#### Response Body

```typescript
interface TransparencyStatisticsResponse {
  total_executions_tracked: number;
  average_transparency_score: number;
  validation_success_rate: number;
  most_used_sources: Record<string, number>;  // source -> usage count
  source_reliability_distribution: Record<string, number>;  // bucket -> count
  data_retention_days: number;
  last_cleanup: string;
  execution_trends: ExecutionTrend[];
}

interface ExecutionTrend {
  date: string;
  executions: number;
  average_transparency: number;
  average_confidence: number;
}
```

---

### GET `/api/v1/transparency/audit/{start_date}/{end_date}`

Get audit report for a specific date range.

#### Path Parameters

- `start_date`: Start date in ISO format (YYYY-MM-DD)
- `end_date`: End date in ISO format (YYYY-MM-DD)

#### Query Parameters

- `agent_filter`: Filter by specific agent
- `domain_filter`: Filter by scientific domain
- `min_transparency`: Minimum transparency score (0.0-1.0)

#### Response Body

```typescript
interface AuditReportResponse {
  period: {
    start: string;
    end: string;
  };
  summary: {
    total_executions: number;
    unique_users: number;
    domains_covered: string[];
    average_transparency: number;
    average_confidence: number;
  };
  executions: ExecutionAudit[];
  anomalies: AuditAnomaly[];
}

interface ExecutionAudit {
  execution_id: string;
  timestamp: string;
  agent: string;
  domain: string;
  transparency_score: number;
  confidence_score: number;
  duration: number;
  sources_used: number;
  warnings: string[];
}

interface AuditAnomaly {
  type: "low_transparency" | "high_duration" | "failed_validation";
  execution_id: string;
  description: string;
  severity: "low" | "medium" | "high";
  recommended_action: string;
}
```

---

## System Management Endpoints

### GET `/api/v1/grokopedia/scientific-capabilities`

Get comprehensive overview of scientific capabilities.

#### Response Body

```typescript
interface ScientificCapabilitiesResponse {
  capabilities: {
    available_domains: string[];
    collaboration_modes: string[];
    knowledge_sources: string[];
    specialized_agents: Record<string, AgentCapabilities>;
  };
  metrics: {
    scientific_agent_usage: Record<string, AgentUsageStats>;
    cross_domain_collaborations: number;
    first_principles_applications: number;
    external_knowledge_queries: number;
    scientific_accuracy_score: number;
  };
  knowledge_integrator_status: "available" | "unavailable";
  supported_domains: string[];
  first_principles_enabled: boolean;
  external_sources_integrated: boolean;
}

interface AgentUsageStats {
  executions: number;
  total_cost: number;
  error_rate: number;
  success_rate: number;
  average_confidence: number;
}
```

---

### GET `/api/v1/grokopedia/scientific-health`

Get real-time health status of the scientific knowledge system.

#### Response Body

```typescript
interface ScientificHealthResponse {
  overall_status: "healthy" | "degraded" | "error";
  timestamp: string;
  agent_status: Record<string, AgentHealth>;
  knowledge_integrator: Record<string, APIHealth>;
  scientific_routing: "enabled" | "disabled";
  first_principles_reasoning: "active" | "inactive";
  system_load: SystemLoadMetrics;
  recent_errors: SystemError[];
}

interface AgentHealth {
  registered: boolean;
  capabilities: number;
  last_execution: string;
  error_rate: number;
  average_response_time: number;
}

interface APIHealth {
  status: "healthy" | "degraded" | "error";
  response_time?: number;
  last_check: string;
  error_count: number;
}

interface SystemLoadMetrics {
  active_executions: number;
  queue_size: number;
  memory_usage_percent: number;
  cpu_usage_percent: number;
}

interface SystemError {
  timestamp: string;
  component: string;
  error_type: string;
  description: string;
  resolved: boolean;
}
```

---

## Error Handling

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (missing/invalid authentication)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (resource doesn't exist)
- `422`: Unprocessable Entity (validation error)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error
- `503`: Service Unavailable (system overload)

### Error Response Format

```typescript
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
    request_id: string;
  };
  context?: {
    component: string;
    operation: string;
    parameters: Record<string, any>;
  };
}
```

### Common Error Codes

- `INVALID_QUERY`: Query format or parameters invalid
- `AGENT_UNAVAILABLE`: Requested agent not available
- `EXTERNAL_API_ERROR`: External knowledge source failed
- `VALIDATION_FAILED`: Scientific claim validation failed
- `TRANSPARENCY_ERROR`: Transparency tracking failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SYSTEM_OVERLOAD`: System capacity exceeded

## Rate Limiting

```typescript
// Rate limits by endpoint
const RATE_LIMITS = {
  "scientific-query": { per_minute: 60, per_hour: 1000 },
  "first-principles-analysis": { per_minute: 30, per_hour: 500 },
  "scientific-validation": { per_minute: 45, per_hour: 750 },
  "transparency-report": { per_minute: 120, per_hour: 5000 },
  "scientific-health": { per_minute: 60, per_hour: 1000 }
};
```

## WebSocket Support

### Real-time Transparency Updates

```javascript
// Connect to transparency WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/transparency');

// Listen for execution updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  if (update.type === 'execution_complete') {
    console.log('Execution completed:', update.execution_id);
    console.log('Transparency score:', update.transparency_score);
  }
};

// Subscribe to specific execution
ws.send(JSON.stringify({
  type: 'subscribe',
  execution_id: 'sci_12345'
}));
```

## SDK Examples

### Python SDK

```python
from nexus_lang_v2 import ScientificClient

# Initialize client
client = ScientificClient(api_key="your_key")

# Scientific query
result = client.scientific_query(
    query="How does quantum tunneling work?",
    domain_focus="physics",
    require_collaboration=True
)

print(f"Confidence: {result.confidence_score}")
for insight in result.analysis_result.key_insights:
    print(f"• {insight}")

# First principles analysis
analysis = client.first_principles_analysis(
    topic="electromagnetism",
    domain="physics",
    depth="comprehensive"
)

print("Fundamental principles:")
for principle in analysis.fundamental_principles:
    print(f"• {principle}")
```

### JavaScript SDK

```javascript
import { NexusLangV2 } from 'nexus-lang-v2-sdk';

const client = new NexusLangV2({ apiKey: 'your_key' });

// Scientific validation
const validation = await client.validateScientificClaim({
  claim: "The speed of light is constant in vacuum",
  domain: "physics",
  evidence_types: ["experimental", "theoretical"]
});

console.log(`Validation: ${validation.result}`);
console.log(`Confidence: ${validation.confidence_score}`);

// Real-time monitoring
client.onTransparencyUpdate((update) => {
  console.log('Execution update:', update);
});
```

## Best Practices

### Query Optimization

1. **Be Specific**: Use precise scientific terminology
2. **Specify Domain**: Use `domain_focus` for better routing
3. **Enable Collaboration**: Set `require_collaboration: true` for complex topics
4. **Include Context**: Provide additional context when available

### Error Handling

```python
try:
    result = client.scientific_query(query="complex scientific question")
    if result.confidence_score < 0.7:
        print("Low confidence - consider refining query")
except Exception as e:
    if "rate_limit" in str(e):
        time.sleep(60)  # Wait for rate limit reset
        retry_query()
    elif "agent_unavailable" in str(e):
        fallback_to_general_ai()
    else:
        log_error_and_notify_user(e)
```

### Performance Considerations

1. **Cache Results**: Reuse results for similar queries
2. **Batch Requests**: Use batch endpoints for multiple queries
3. **Monitor Usage**: Track API usage and optimize accordingly
4. **Async Processing**: Use async endpoints for long-running analyses

---

## Support

For API support, visit:
- [API Documentation](https://docs.nexus-lang-v2.com)
- [GitHub Issues](https://github.com/nexus-lang-v2/issues)
- [Developer Community](https://community.nexus-lang-v2.com)

**Version**: 2.0.0
**Last Updated**: November 2025
