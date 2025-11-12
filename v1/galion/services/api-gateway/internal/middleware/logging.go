// Package middleware provides HTTP middleware functions
package middleware

import (
	"net/http"
	"time"

	"nexus-api-gateway/pkg/logger"
)

// responseWriter is a wrapper around http.ResponseWriter to capture status code
type responseWriter struct {
	http.ResponseWriter
	statusCode int
}

// WriteHeader captures the status code
func (rw *responseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}

// Logging middleware logs all HTTP requests with timing information
func Logging(log *logger.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			
			// Wrap the response writer to capture status code
			wrapped := &responseWriter{
				ResponseWriter: w,
				statusCode:     http.StatusOK, // Default status
			}
			
			// Process request
			next.ServeHTTP(wrapped, r)
			
			// Log request details
			duration := time.Since(start)
			log.Info(
				"%s %s - %d - %s - %s",
				r.Method,
				r.RequestURI,
				wrapped.statusCode,
				duration,
				r.RemoteAddr,
			)
		})
	}
}

// RequestID middleware adds a unique request ID to each request
func RequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Get request ID from header or generate new one
		requestID := r.Header.Get("X-Request-ID")
		if requestID == "" {
			requestID = generateRequestID()
		}
		
		// Add request ID to response headers
		w.Header().Set("X-Request-ID", requestID)
		
		// Add to request context for use in handlers
		ctx := r.Context()
		// You can use context.WithValue to store the requestID
		
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// generateRequestID generates a unique request ID
func generateRequestID() string {
	// Simple implementation - in production use UUID or similar
	return time.Now().Format("20060102150405")
}

