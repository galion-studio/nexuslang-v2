// Package metrics provides Prometheus metrics
package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	// EventsProcessed counts the number of events processed by type
	EventsProcessed = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "analytics_events_processed_total",
			Help: "Total number of events processed",
		},
		[]string{"event_type", "service"},
	)

	// EventsProcessingDuration measures event processing time
	EventsProcessingDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "analytics_events_processing_duration_seconds",
			Help:    "Event processing duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"event_type"},
	)

	// EventsProcessingErrors counts processing errors
	EventsProcessingErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "analytics_events_processing_errors_total",
			Help: "Total number of event processing errors",
		},
		[]string{"event_type", "error_type"},
	)

	// ActiveUsers tracks unique active users in the last hour
	ActiveUsers = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "analytics_active_users",
			Help: "Number of unique active users in the last hour",
		},
	)

	// EventsStored tracks total events stored in database
	EventsStored = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "analytics_events_stored_total",
			Help: "Total number of events stored in database",
		},
	)
)

// RecordEventProcessed records a processed event
func RecordEventProcessed(eventType, service string) {
	EventsProcessed.WithLabelValues(eventType, service).Inc()
}

// RecordProcessingError records a processing error
func RecordProcessingError(eventType, errorType string) {
	EventsProcessingErrors.WithLabelValues(eventType, errorType).Inc()
}

// UpdateEventsStored updates the total events stored metric
func UpdateEventsStored(count int64) {
	EventsStored.Set(float64(count))
}

