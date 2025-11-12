// Package middleware provides rate limiting functionality
package middleware

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/redis/go-redis/v9"
)

// RateLimiter provides rate limiting using Redis
type RateLimiter struct {
	client       *redis.Client
	limit        int           // requests per window
	window       time.Duration // time window
	enabled      bool
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(redisClient *redis.Client, requestsPerMinute int, enabled bool) *RateLimiter {
	return &RateLimiter{
		client:  redisClient,
		limit:   requestsPerMinute,
		window:  time.Minute,
		enabled: enabled,
	}
}

// Middleware returns the rate limiting middleware
func (rl *RateLimiter) Middleware() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Skip rate limiting if disabled
			if !rl.enabled {
				next.ServeHTTP(w, r)
				return
			}
			
			// Use IP address as the rate limit key
			// In production, you might want to use user ID for authenticated requests
			clientIP := getClientIP(r)
			key := fmt.Sprintf("ratelimit:%s", clientIP)
			
			ctx := context.Background()
			
			// Check current count
			count, err := rl.client.Get(ctx, key).Int()
			if err != nil && err != redis.Nil {
				// If Redis error, allow the request (fail open)
				next.ServeHTTP(w, r)
				return
			}
			
			// Check if limit exceeded
			if count >= rl.limit {
				w.Header().Set("X-RateLimit-Limit", fmt.Sprintf("%d", rl.limit))
				w.Header().Set("X-RateLimit-Remaining", "0")
				w.WriteHeader(http.StatusTooManyRequests)
				w.Write([]byte(`{"error":"rate limit exceeded"}`))
				return
			}
			
			// Increment counter
			pipe := rl.client.Pipeline()
			incr := pipe.Incr(ctx, key)
			pipe.Expire(ctx, key, rl.window)
			_, err = pipe.Exec(ctx)
			
			if err != nil {
				// If Redis error, allow the request (fail open)
				next.ServeHTTP(w, r)
				return
			}
			
			// Add rate limit headers
			newCount := int(incr.Val())
			remaining := rl.limit - newCount
			if remaining < 0 {
				remaining = 0
			}
			
			w.Header().Set("X-RateLimit-Limit", fmt.Sprintf("%d", rl.limit))
			w.Header().Set("X-RateLimit-Remaining", fmt.Sprintf("%d", remaining))
			
			// Process request
			next.ServeHTTP(w, r)
		})
	}
}

// getClientIP extracts the client IP address from the request
func getClientIP(r *http.Request) string {
	// Check X-Forwarded-For header first (for requests behind proxy)
	xff := r.Header.Get("X-Forwarded-For")
	if xff != "" {
		return xff
	}
	
	// Check X-Real-IP header
	xri := r.Header.Get("X-Real-IP")
	if xri != "" {
		return xri
	}
	
	// Fall back to RemoteAddr
	return r.RemoteAddr
}

