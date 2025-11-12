// Main entry point for Analytics Service
package main

import (
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/joho/godotenv"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	"nexus-analytics-service/internal/consumer"
	"nexus-analytics-service/internal/storage"
	"nexus-analytics-service/pkg/metrics"
)

func main() {
	// Load environment variables
	godotenv.Load()

	log.Println("Starting Nexus Analytics Service...")

	// Configuration from environment
	kafkaBrokers := getEnv("KAFKA_BROKERS", "localhost:9092")
	databaseURL := getEnv("DATABASE_URL", "postgres://nexuscore:nexuscore123@localhost:5432/nexuscore")
	metricsPort := getEnv("METRICS_PORT", "9090")

	// Initialize event store (PostgreSQL)
	log.Println("Connecting to database...")
	eventStore, err := storage.NewEventStore(databaseURL)
	if err != nil {
		log.Fatalf("Failed to initialize event store: %v", err)
	}
	defer eventStore.Close()
	log.Println("Connected to database")

	// Create event handler
	eventHandler := func(event *consumer.Event) error {
		// Parse timestamp
		timestamp, err := time.Parse(time.RFC3339, event.Timestamp)
		if err != nil {
			log.Printf("Failed to parse timestamp: %v", err)
			timestamp = time.Now()
		}

		// Save event to database
		err = eventStore.SaveEvent(
			event.EventType,
			event.UserID,
			event.Service,
			timestamp,
			event.Data,
		)
		if err != nil {
			metrics.RecordProcessingError(event.EventType, "storage_error")
			return err
		}

		// Update metrics
		metrics.RecordEventProcessed(event.EventType, event.Service)

		log.Printf("Processed event: %s (user: %s)", event.EventType, event.UserID)
		return nil
	}

	// Initialize Kafka consumer
	log.Println("Initializing Kafka consumer...")
	kafkaConsumer, err := consumer.NewKafkaConsumer(
		kafkaBrokers,
		"analytics-service",
		[]string{"user-events"},
		eventHandler,
	)
	if err != nil {
		log.Fatalf("Failed to initialize Kafka consumer: %v", err)
	}
	defer kafkaConsumer.Close()
	log.Println("Kafka consumer initialized")

	// Start Prometheus metrics endpoint
	go func() {
		http.Handle("/metrics", promhttp.Handler())
		http.HandleFunc("/health", healthCheckHandler)
		log.Printf("Metrics server listening on :%s", metricsPort)
		if err := http.ListenAndServe(":"+metricsPort, nil); err != nil {
			log.Fatalf("Failed to start metrics server: %v", err)
		}
	}()

	// Start background task to update metrics
	go func() {
		ticker := time.NewTicker(30 * time.Second)
		defer ticker.Stop()

		for range ticker.C {
			count, err := eventStore.GetEventCount()
			if err != nil {
				log.Printf("Failed to get event count: %v", err)
				continue
			}
			metrics.UpdateEventsStored(count)
		}
	}()

	// Start consuming events (blocking)
	go func() {
		if err := kafkaConsumer.Start(); err != nil {
			log.Fatalf("Kafka consumer error: %v", err)
		}
	}()

	// Wait for interrupt signal
	sigterm := make(chan os.Signal, 1)
	signal.Notify(sigterm, syscall.SIGINT, syscall.SIGTERM)
	<-sigterm

	log.Println("Shutting down analytics service...")
}

// getEnv gets an environment variable or returns a default value
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

// healthCheckHandler handles health check requests
func healthCheckHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"status":"healthy","service":"analytics-service"}`))
}

