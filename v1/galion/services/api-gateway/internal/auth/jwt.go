// Package auth handles JWT token verification
package auth

import (
	"errors"
	"fmt"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

var (
	// ErrMissingToken is returned when no token is provided
	ErrMissingToken = errors.New("missing authorization token")
	
	// ErrInvalidToken is returned when token is invalid
	ErrInvalidToken = errors.New("invalid authorization token")
	
	// ErrExpiredToken is returned when token is expired
	ErrExpiredToken = errors.New("token has expired")
)

// JWTValidator handles JWT token validation
type JWTValidator struct {
	secretKey string
	algorithm string
}

// NewJWTValidator creates a new JWT validator
func NewJWTValidator(secretKey, algorithm string) *JWTValidator {
	return &JWTValidator{
		secretKey: secretKey,
		algorithm: algorithm,
	}
}

// ExtractToken extracts the JWT token from Authorization header
// Expected format: "Bearer <token>"
func ExtractToken(authHeader string) (string, error) {
	if authHeader == "" {
		return "", ErrMissingToken
	}
	
	// Check if header starts with "Bearer "
	parts := strings.Split(authHeader, " ")
	if len(parts) != 2 || parts[0] != "Bearer" {
		return "", ErrInvalidToken
	}
	
	return parts[1], nil
}

// ValidateToken validates a JWT token and returns the claims
func (v *JWTValidator) ValidateToken(tokenString string) (*jwt.MapClaims, error) {
	// Parse the token
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		// Verify the signing method
		if token.Method.Alg() != v.algorithm {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		
		return []byte(v.secretKey), nil
	})
	
	if err != nil {
		// Check if error is due to expiration
		if errors.Is(err, jwt.ErrTokenExpired) {
			return nil, ErrExpiredToken
		}
		return nil, ErrInvalidToken
	}
	
	// Check if token is valid
	if !token.Valid {
		return nil, ErrInvalidToken
	}
	
	// Extract claims
	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, ErrInvalidToken
	}
	
	return &claims, nil
}

// GetUserEmail extracts the user email from JWT claims
// The email is stored in the "sub" (subject) claim
func GetUserEmail(claims *jwt.MapClaims) (string, error) {
	sub, ok := (*claims)["sub"]
	if !ok {
		return "", errors.New("missing subject claim")
	}
	
	email, ok := sub.(string)
	if !ok {
		return "", errors.New("invalid subject claim type")
	}
	
	return email, nil
}

