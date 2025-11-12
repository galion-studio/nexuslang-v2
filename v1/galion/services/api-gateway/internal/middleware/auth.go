// Package middleware provides authentication middleware
package middleware

import (
	"net/http"

	"nexus-api-gateway/internal/auth"
	"nexus-api-gateway/pkg/logger"
)

// AuthMiddleware provides JWT authentication middleware
type AuthMiddleware struct {
	validator *auth.JWTValidator
	logger    *logger.Logger
}

// NewAuthMiddleware creates a new authentication middleware
func NewAuthMiddleware(validator *auth.JWTValidator, log *logger.Logger) *AuthMiddleware {
	return &AuthMiddleware{
		validator: validator,
		logger:    log,
	}
}

// Require returns middleware that requires valid JWT token
func (am *AuthMiddleware) Require() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Extract token from Authorization header
			authHeader := r.Header.Get("Authorization")
			token, err := auth.ExtractToken(authHeader)
			
			if err != nil {
				am.logger.Debug("Authentication failed: %v", err)
				w.WriteHeader(http.StatusUnauthorized)
				w.Write([]byte(`{"error":"unauthorized","message":"missing or invalid token"}`))
				return
			}
			
			// Validate token
			claims, err := am.validator.ValidateToken(token)
			if err != nil {
				am.logger.Debug("Token validation failed: %v", err)
				w.WriteHeader(http.StatusUnauthorized)
				w.Write([]byte(`{"error":"unauthorized","message":"invalid or expired token"}`))
				return
			}
			
			// Extract user email from claims
			email, err := auth.GetUserEmail(claims)
			if err != nil {
				am.logger.Error("Failed to extract email from token: %v", err)
				w.WriteHeader(http.StatusUnauthorized)
				w.Write([]byte(`{"error":"unauthorized","message":"invalid token claims"}`))
				return
			}
			
			// Add user email to request header for backend services
			r.Header.Set("X-User-Email", email)
			
			// Process request
			next.ServeHTTP(w, r)
		})
	}
}

// Optional returns middleware that allows but doesn't require authentication
// If token is present and valid, user info is added to headers
func (am *AuthMiddleware) Optional() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Try to extract token
			authHeader := r.Header.Get("Authorization")
			if authHeader != "" {
				token, err := auth.ExtractToken(authHeader)
				if err == nil {
					// Validate token
					claims, err := am.validator.ValidateToken(token)
					if err == nil {
						// Extract user email
						email, err := auth.GetUserEmail(claims)
						if err == nil {
							// Add user email to headers
							r.Header.Set("X-User-Email", email)
						}
					}
				}
			}
			
			// Process request (with or without auth)
			next.ServeHTTP(w, r)
		})
	}
}

