/**
 * K6 Spike Test for GALION APIs
 * Simulates sudden traffic spikes
 * 
 * Usage:
 *   k6 run tests/load/spike-test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    // Normal load
    { duration: '2m', target: 100 },
    
    // Sudden spike (simulates going viral, HN front page, etc.)
    { duration: '30s', target: 1000 },  // 10x spike
    { duration: '3m', target: 1000 },   // Maintain spike
    
    // Return to normal
    { duration: '1m', target: 100 },
    { duration: '2m', target: 100 },
    
    // Shutdown
    { duration: '1m', target: 0 },
  ],
  
  thresholds: {
    'http_req_duration': ['p(95)<1000'],
    'http_req_failed': ['rate<0.10'],  // Allow 10% failure during spike
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://api.galion.app';

export default function() {
  let res = http.get(`${BASE_URL}/health`);
  
  check(res, {
    'status OK': (r) => r.status === 200,
  });
  
  sleep(1);
}

export function teardown() {
  console.log('Spike test complete. Check if auto-healing kicked in.');
}

