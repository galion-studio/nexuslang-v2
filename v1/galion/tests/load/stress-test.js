/**
 * K6 Stress Test for GALION APIs
 * Pushes system to limits to find breaking point
 * 
 * Usage:
 *   k6 run tests/load/stress-test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    // Gradually increase load
    { duration: '2m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '2m', target: 400 },
    { duration: '2m', target: 600 },
    { duration: '2m', target: 800 },
    { duration: '3m', target: 1000 },  // Push to 1000 concurrent users
    
    // Maintain peak
    { duration: '5m', target: 1000 },
    
    // Cool down
    { duration: '2m', target: 0 },
  ],
  
  thresholds: {
    // More lenient thresholds for stress testing
    'http_req_duration': ['p(95)<2000'],  // 95% < 2s
    'http_req_failed': ['rate<0.05'],     // < 5% failure rate
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://api.galion.app';

export default function() {
  let res = http.get(`${BASE_URL}/health`);
  
  check(res, {
    'status is 200 or 503': (r) => r.status === 200 || r.status === 503,
  });
  
  sleep(0.5);  // More aggressive request rate
}

export function teardown(data) {
  console.log('Stress test complete. Review Grafana for system behavior under load.');
}

