// Package consumer handles Kafka event consumption
package consumer

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

// Event represents a user event from Kafka
type Event struct {
	EventType string                 `json:"event_type"`
	UserID    string                 `json:"user_id"`
	Timestamp string                 `json:"timestamp"`
	Service   string                 `json:"service"`
	Data      map[string]interface{} `json:"data"`
}

// EventHandler is a function that processes events
type EventHandler func(*Event) error

// KafkaConsumer consumes events from Kafka
type KafkaConsumer struct {
	consumer *kafka.Consumer
	topics   []string
	handler  EventHandler
}

// NewKafkaConsumer creates a new Kafka consumer
func NewKafkaConsumer(brokers string, groupID string, topics []string, handler EventHandler) (*KafkaConsumer, error) {
	config := &kafka.ConfigMap{
		"bootstrap.servers": brokers,
		"group.id":          groupID,
		"auto.offset.reset": "earliest", // Start from beginning if no offset
	}

	consumer, err := kafka.NewConsumer(config)
	if err != nil {
		return nil, fmt.Errorf("failed to create consumer: %w", err)
	}

	// Subscribe to topics
	err = consumer.SubscribeTopics(topics, nil)
	if err != nil {
		consumer.Close()
		return nil, fmt.Errorf("failed to subscribe to topics: %w", err)
	}

	log.Printf("Subscribed to topics: %v", topics)

	return &KafkaConsumer{
		consumer: consumer,
		topics:   topics,
		handler:  handler,
	}, nil
}

// Start begins consuming events
// This is a blocking call that runs until stopped
func (kc *KafkaConsumer) Start() error {
	log.Println("Starting Kafka consumer...")

	for {
		// Poll for messages
		msg, err := kc.consumer.ReadMessage(time.Second * 1)
		if err != nil {
			// Check if it's just a timeout (no message available)
			if kafkaErr, ok := err.(kafka.Error); ok && kafkaErr.Code() == kafka.ErrTimedOut {
				continue
			}
			log.Printf("Error reading message: %v", err)
			continue
		}

		// Parse the event
		var event Event
		err = json.Unmarshal(msg.Value, &event)
		if err != nil {
			log.Printf("Failed to unmarshal event: %v", err)
			continue
		}

		// Log the event
		log.Printf("Received event: %s from %s (user: %s)", event.EventType, event.Service, event.UserID)

		// Handle the event
		err = kc.handler(&event)
		if err != nil {
			log.Printf("Failed to handle event %s: %v", event.EventType, err)
			// Don't commit offset if handling failed
			continue
		}

		// Commit offset after successful processing
		_, err = kc.consumer.CommitMessage(msg)
		if err != nil {
			log.Printf("Failed to commit offset: %v", err)
		}
	}
}

// Close closes the Kafka consumer
func (kc *KafkaConsumer) Close() error {
	if kc.consumer != nil {
		return kc.consumer.Close()
	}
	return nil
}

