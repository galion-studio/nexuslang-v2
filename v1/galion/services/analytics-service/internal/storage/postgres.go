// Package storage handles database operations for analytics
package storage

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	_ "github.com/lib/pq"
)

// EventStore stores events in PostgreSQL
type EventStore struct {
	db *sql.DB
}

// NewEventStore creates a new event store
func NewEventStore(databaseURL string) (*EventStore, error) {
	// Add SSL mode to connection string if not present
	// PostgreSQL in Docker doesn't have SSL enabled by default
	if databaseURL != "" && !contains(databaseURL, "sslmode=") {
		if contains(databaseURL, "?") {
			databaseURL += "&sslmode=disable"
		} else {
			databaseURL += "?sslmode=disable"
		}
	}
	
	// Connect to database
	db, err := sql.Open("postgres", databaseURL)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// Test connection
	err = db.Ping()
	if err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	// Ensure analytics schema exists
	_, err = db.Exec(`CREATE SCHEMA IF NOT EXISTS analytics`)
	if err != nil {
		return nil, fmt.Errorf("failed to create analytics schema: %w", err)
	}

	// Create events table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS analytics.events (
			id SERIAL PRIMARY KEY,
			event_type VARCHAR(100) NOT NULL,
			user_id VARCHAR(100) NOT NULL,
			service VARCHAR(50) NOT NULL,
			timestamp TIMESTAMP NOT NULL,
			data JSONB,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		return nil, fmt.Errorf("failed to create events table: %w", err)
	}

	// Create indexes separately (PostgreSQL doesn't support INDEX in CREATE TABLE)
	indexes := []string{
		"CREATE INDEX IF NOT EXISTS idx_event_type ON analytics.events(event_type)",
		"CREATE INDEX IF NOT EXISTS idx_user_id ON analytics.events(user_id)",
		"CREATE INDEX IF NOT EXISTS idx_timestamp ON analytics.events(timestamp)",
	}

	for _, indexSQL := range indexes {
		_, err = db.Exec(indexSQL)
		if err != nil {
			// Log error but don't fail - indexes are optional for functionality
			fmt.Printf("Warning: Failed to create index: %v\n", err)
		}
	}

	return &EventStore{db: db}, nil
}

// SaveEvent saves an event to the database
func (es *EventStore) SaveEvent(eventType, userID, service string, timestamp time.Time, data map[string]interface{}) error {
	// Convert data map to JSON
	dataJSON, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("failed to marshal data: %w", err)
	}

	// Insert event into database
	query := `
		INSERT INTO analytics.events (event_type, user_id, service, timestamp, data)
		VALUES ($1, $2, $3, $4, $5)
	`

	_, err = es.db.Exec(query, eventType, userID, service, timestamp, dataJSON)
	if err != nil {
		return fmt.Errorf("failed to insert event: %w", err)
	}

	return nil
}

// GetEventCount returns the total number of events
func (es *EventStore) GetEventCount() (int64, error) {
	var count int64
	err := es.db.QueryRow("SELECT COUNT(*) FROM analytics.events").Scan(&count)
	if err != nil {
		return 0, err
	}
	return count, nil
}

// GetEventCountByType returns event counts grouped by type
func (es *EventStore) GetEventCountByType() (map[string]int64, error) {
	rows, err := es.db.Query(`
		SELECT event_type, COUNT(*) as count
		FROM analytics.events
		GROUP BY event_type
		ORDER BY count DESC
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	result := make(map[string]int64)
	for rows.Next() {
		var eventType string
		var count int64
		err := rows.Scan(&eventType, &count)
		if err != nil {
			return nil, err
		}
		result[eventType] = count
	}

	return result, nil
}

// Close closes the database connection
func (es *EventStore) Close() error {
	return es.db.Close()
}

// contains checks if a string contains a substring
func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > len(substr) && 
		(s[:len(substr)] == substr || s[len(s)-len(substr):] == substr || 
		containsMiddle(s, substr)))
}

func containsMiddle(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

