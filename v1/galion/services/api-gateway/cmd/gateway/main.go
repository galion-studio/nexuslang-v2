// Main entry point for API Gateway
package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	"github.com/redis/go-redis/v9"
	"github.com/rs/cors"

	"nexus-api-gateway/internal/auth"
	"nexus-api-gateway/internal/middleware"
	"nexus-api-gateway/internal/proxy"
	"nexus-api-gateway/pkg/logger"
)

// Config holds application configuration
type Config struct {
	Port                   string
	Environment            string
	Debug                  bool
	JWTSecretKey          string
	JWTAlgorithm          string
	AuthServiceURL        string
	UserServiceURL        string
	ContentServiceURL     string
	RedisURL              string
	RateLimitEnabled      bool
	RateLimitPerMinute    int
	AllowedOrigins        []string
}

func main() {
	// Load environment variables
	godotenv.Load()
	
	// Load configuration
	config := loadConfig()
	
	// Initialize logger
	log := logger.New(config.Debug)
	log.Info("Starting Nexus API Gateway")
	log.Info("Environment: %s", config.Environment)
	
	// Initialize Redis client
	redisOpts, err := redis.ParseURL(config.RedisURL)
	if err != nil {
		log.Fatal("Failed to parse Redis URL: %v", err)
	}
	redisClient := redis.NewClient(redisOpts)
	
	// Test Redis connection
	ctx := context.Background()
	if err := redisClient.Ping(ctx).Err(); err != nil {
		log.Warn("Failed to connect to Redis: %v (rate limiting disabled)", err)
		config.RateLimitEnabled = false
	} else {
		log.Info("Connected to Redis")
	}
	
	// Initialize JWT validator
	jwtValidator := auth.NewJWTValidator(config.JWTSecretKey, config.JWTAlgorithm)
	
	// Initialize middleware
	authMiddleware := middleware.NewAuthMiddleware(jwtValidator, log)
	rateLimiter := middleware.NewRateLimiter(redisClient, config.RateLimitPerMinute, config.RateLimitEnabled)
	
	// Initialize proxy
	serviceProxy := proxy.NewServiceProxy(log)
	
	// Create router
	router := mux.NewRouter()
	
	// Health check endpoint (no auth required)
	router.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"healthy","service":"api-gateway"}`))
	}).Methods("GET")
	
	// Metrics endpoint for Prometheus (no auth required)
	router.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("# HELP api_gateway_up API Gateway status\n"))
		w.Write([]byte("# TYPE api_gateway_up gauge\n"))
		w.Write([]byte("api_gateway_up 1\n"))
	}).Methods("GET")
	
	// Auth service routes (no auth required for login/register)
	// Handle all HTTP methods including OPTIONS for CORS preflight
	authRouter := router.PathPrefix("/api/v1/auth").Subrouter()
	authRouter.PathPrefix("").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		serviceProxy.ProxyRequest(w, r, config.AuthServiceURL)
	}).Methods("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
	
	// User service routes (require authentication)
	// Handle all HTTP methods including OPTIONS for CORS preflight
	userRouter := router.PathPrefix("/api/v1/users").Subrouter()
	userRouter.Use(authMiddleware.Require())
	userRouter.PathPrefix("").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		serviceProxy.ProxyRequest(w, r, config.UserServiceURL)
	}).Methods("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
	
	// Content service routes (require authentication)
	// Handle all HTTP methods including OPTIONS for CORS preflight
	contentRouter := router.PathPrefix("/api/v1/content").Subrouter()
	contentRouter.Use(authMiddleware.Require())
	contentRouter.PathPrefix("").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		serviceProxy.ProxyRequest(w, r, config.ContentServiceURL)
	}).Methods("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
	
	// Apply global middleware
	handler := middleware.RequestID(router)
	handler = middleware.Logging(log)(handler)
	handler = rateLimiter.Middleware()(handler)
	
	// Apply CORS
	corsHandler := cors.New(cors.Options{
		AllowedOrigins:   config.AllowedOrigins,
		AllowedMethods:   []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"*"},
		AllowCredentials: true,
		MaxAge:           300, // Cache preflight requests for 5 minutes
	}).Handler(handler)
	
	// Create HTTP server
	server := &http.Server{
		Addr:         ":" + config.Port,
		Handler:      corsHandler,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}
	
	// Start server in a goroutine
	go func() {
		log.Info("API Gateway listening on port %s", config.Port)
		log.Info("Auth Service: %s", config.AuthServiceURL)
		log.Info("User Service: %s", config.UserServiceURL)
		log.Info("Content Service: %s", config.ContentServiceURL)
		
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal("Failed to start server: %v", err)
		}
	}()
	
	// Wait for interrupt signal to gracefully shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	
	log.Info("Shutting down server...")
	
	// Graceful shutdown with 5 second timeout
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	if err := server.Shutdown(ctx); err != nil {
		log.Error("Server forced to shutdown: %v", err)
	}
	
	// Close Redis connection
	redisClient.Close()
	
	log.Info("Server stopped")
}

// loadConfig loads configuration from environment variables
func loadConfig() *Config {
	return &Config{
		Port:               getEnv("PORT", "8080"),
		Environment:        getEnv("ENVIRONMENT", "development"),
		Debug:              getEnvBool("DEBUG", true),
		JWTSecretKey:       getEnv("JWT_SECRET_KEY", "dev-secret-key-change-this-in-production"),
		JWTAlgorithm:       getEnv("JWT_ALGORITHM", "HS256"),
		AuthServiceURL:     getEnv("AUTH_SERVICE_URL", "http://localhost:8000"),
		UserServiceURL:     getEnv("USER_SERVICE_URL", "http://localhost:8001"),
		ContentServiceURL:   getEnv("CONTENT_SERVICE_URL", "http://localhost:8002"),
		RedisURL:           getEnv("REDIS_URL", "redis://localhost:6379/0"),
		RateLimitEnabled:   getEnvBool("RATE_LIMIT_ENABLED", true),
		RateLimitPerMinute: getEnvInt("RATE_LIMIT_REQUESTS_PER_MINUTE", 60),
		AllowedOrigins:     getEnvSlice("ALLOWED_ORIGINS", []string{"http://localhost:3000"}),
	}
}

// getEnv gets an environment variable or returns a default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

// getEnvBool gets a boolean environment variable or returns a default value
func getEnvBool(key string, defaultValue bool) bool {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	
	boolValue, err := strconv.ParseBool(value)
	if err != nil {
		return defaultValue
	}
	
	return boolValue
}

// getEnvInt gets an integer environment variable or returns a default value
func getEnvInt(key string, defaultValue int) int {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	
	intValue, err := strconv.Atoi(value)
	if err != nil {
		return defaultValue
	}
	
	return intValue
}

// getEnvSlice gets a comma-separated environment variable as a slice
func getEnvSlice(key string, defaultValue []string) []string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	
	return strings.Split(value, ",")
}

