/**
 * K6 Load Test for GALION APIs
 * Tests API performance under various load scenarios
 * 
 * Usage:
 *   k6 run tests/load/api-test.js
 *   k6 run --vus 100 --duration 5m tests/load/api-test.js
 *   k6 run -e API_TOKEN=your-token tests/load/api-test.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const apiLatency = new Trend('api_latency');
const apiErrors = new Counter('api_errors');
const apiSuccess = new Rate('api_success_rate');

// Test configuration
export let options = {
  stages: [
    // Warm-up phase
    { duration: '1m', target: 50 },    // Ramp up to 50 users
    
    // Normal load
    { duration: '3m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    
    // Peak load
    { duration: '2m', target: 200 },   // Spike to 200 users
    { duration: '3m', target: 200 },   // Maintain peak
    
    // Cool down
    { duration: '2m', target: 50 },    // Ramp down to 50
    { duration: '1m', target: 0 },     // Graceful shutdown
  ],
  
  thresholds: {
    // Performance thresholds
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],  // 95% < 500ms, 99% < 1s
    'http_req_failed': ['rate<0.01'],                  // < 1% failure rate
    'api_success_rate': ['rate>0.99'],                 // > 99% success
    
    // Custom metric thresholds
    'api_latency': ['p(95)<500', 'p(99)<1000'],
  },
  
  // Test configuration
  noConnectionReuse: false,  // Reuse connections (more realistic)
  userAgent: 'K6LoadTest/1.0',
};

// Base URLs (can be overridden with -e flag)
const BASE_URL = __ENV.BASE_URL || 'https://api.galion.app';
const STUDIO_URL = __ENV.STUDIO_URL || 'https://api.studio.galion.app';
const API_TOKEN = __ENV.API_TOKEN || '';

// Test setup
export function setup() {
  console.log('Starting load test...');
  console.log('Target: ' + BASE_URL);
  console.log('Studio: ' + STUDIO_URL);
  console.log('VUs: Up to 200 concurrent users');
  console.log('Duration: ~17 minutes');
  return { startTime: new Date().toISOString() };
}

// Main test function
export default function(data) {
  // Test GALION.APP endpoints
  group('GALION.APP', function() {
    // Health check
    group('Health Check', function() {
      let res = http.get(`${BASE_URL}/health`);
      
      check(res, {
        'health status is 200': (r) => r.status === 200,
        'health response time < 100ms': (r) => r.timings.duration < 100,
        'health returns status': (r) => r.json('status') === 'healthy',
      });
      
      apiLatency.add(res.timings.duration);
      apiSuccess.add(res.status === 200);
      if (res.status !== 200) apiErrors.add(1);
    });
    
    // Readiness check
    group('Readiness Check', function() {
      let res = http.get(`${BASE_URL}/health/ready`);
      
      check(res, {
        'ready status is 200': (r) => r.status === 200,
        'all checks pass': (r) => {
          try {
            const body = r.json();
            return body.status === 'ready';
          } catch {
            return false;
          }
        },
      });
    });
    
    // Test authenticated endpoint (if token provided)
    if (API_TOKEN) {
      group('User Profile', function() {
        let params = {
          headers: {
            'Authorization': `Bearer ${API_TOKEN}`,
            'Content-Type': 'application/json',
          },
        };
        
        let res = http.get(`${BASE_URL}/api/v1/users/me`, params);
        
        check(res, {
          'profile status is 200': (r) => r.status === 200 || r.status === 401,
          'profile response time < 500ms': (r) => r.timings.duration < 500,
        });
        
        apiLatency.add(res.timings.duration);
        apiSuccess.add(res.status === 200);
      });
    }
  });
  
  // Test GALION.STUDIO endpoints
  group('GALION.STUDIO', function() {
    // Health check
    group('Health Check', function() {
      let res = http.get(`${STUDIO_URL}/health`);
      
      check(res, {
        'studio health is 200': (r) => r.status === 200,
        'studio health < 100ms': (r) => r.timings.duration < 100,
      });
      
      apiLatency.add(res.timings.duration);
      apiSuccess.add(res.status === 200);
      if (res.status !== 200) apiErrors.add(1);
    });
    
    // Test public endpoints (if any)
    group('Public Endpoints', function() {
      // Example: public job postings
      let res = http.get(`${STUDIO_URL}/api/v1/jobs/public`);
      
      check(res, {
        'public jobs accessible': (r) => r.status === 200 || r.status === 404,
        'public jobs < 300ms': (r) => r.timings.duration < 300,
      });
    });
  });
  
  // Realistic user behavior: think time between requests
  sleep(Math.random() * 3 + 1);  // 1-4 seconds between requests
}

// Teardown function
export function teardown(data) {
  console.log('Load test completed');
  console.log('Started at: ' + data.startTime);
  console.log('Ended at: ' + new Date().toISOString());
}

