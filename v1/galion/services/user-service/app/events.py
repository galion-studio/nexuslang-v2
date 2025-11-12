"""
Event publishing to Kafka for analytics and monitoring.
All user actions are published as events for downstream processing.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

from app.config import settings


logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Publishes events to Kafka for analytics and monitoring.
    
    Events are published asynchronously to avoid blocking API requests.
    If Kafka is unavailable, events are logged but requests continue.
    """
    
    def __init__(self):
        """Initialize Kafka producer."""
        self.producer: Optional[KafkaProducer] = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        """
        Initialize Kafka producer with retry logic.
        
        If Kafka is not available, log error and continue.
        The application should work even without Kafka.
        """
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            logger.warning("Events will not be published to Kafka")
            self.producer = None
    
    def publish_event(
        self,
        event_type: str,
        user_id: str,
        data: Dict[str, Any],
        topic: str = "user-events"
    ):
        """
        Publish an event to Kafka.
        
        Args:
            event_type: Type of event (e.g., "user.profile_updated")
            user_id: User ID associated with the event
            data: Event data (will be serialized to JSON)
            topic: Kafka topic to publish to
        """
        if not self.producer:
            logger.debug(f"Kafka not available, skipping event: {event_type}")
            return
        
        try:
            # Create event payload
            # Use RFC3339 format (ISO8601 with 'Z' suffix) for compatibility with Go parser
            event = {
                "event_type": event_type,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "service": "user-service",
                "data": data
            }
            
            # Publish to Kafka
            future = self.producer.send(
                topic,
                key=user_id,
                value=event
            )
            
            # Add callback for logging (non-blocking)
            future.add_callback(self._on_send_success, event_type)
            future.add_errback(self._on_send_error, event_type)
            
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
    
    def _on_send_success(self, event_type: str, metadata):
        """Callback when event is successfully published."""
        logger.debug(
            f"Event {event_type} published to topic {metadata.topic} "
            f"partition {metadata.partition} offset {metadata.offset}"
        )
    
    def _on_send_error(self, event_type: str, exception):
        """Callback when event publishing fails."""
        logger.error(f"Failed to publish event {event_type}: {exception}")
    
    def flush(self):
        """Flush pending events (useful for shutdown)."""
        if self.producer:
            try:
                self.producer.flush(timeout=5)
            except Exception as e:
                logger.error(f"Failed to flush Kafka producer: {e}")
    
    def close(self):
        """Close the Kafka producer."""
        if self.producer:
            try:
                self.producer.close(timeout=5)
                logger.info("Kafka producer closed")
            except Exception as e:
                logger.error(f"Failed to close Kafka producer: {e}")


# Global event publisher instance
event_publisher = EventPublisher()


# Event publishing helper functions

def publish_profile_updated(user_id: str, fields_updated: list):
    """Publish profile update event."""
    event_publisher.publish_event(
        event_type="user.profile_updated",
        user_id=user_id,
        data={
            "fields_updated": fields_updated
        }
    )


def publish_profile_viewed(viewer_id: str, viewed_user_id: str):
    """Publish profile view event."""
    event_publisher.publish_event(
        event_type="user.profile_viewed",
        user_id=viewer_id,
        data={
            "viewed_user_id": viewed_user_id
        }
    )


def publish_user_search(user_id: str, query: str, results_count: int):
    """Publish user search event."""
    event_publisher.publish_event(
        event_type="user.search_performed",
        user_id=user_id,
        data={
            "query": query,
            "results_count": results_count
        }
    )


def publish_user_deactivated(admin_id: str, target_user_id: str):
    """Publish user deactivation event."""
    event_publisher.publish_event(
        event_type="user.deactivated",
        user_id=admin_id,
        data={
            "target_user_id": target_user_id
        }
    )


def publish_user_activated(admin_id: str, target_user_id: str):
    """Publish user activation event."""
    event_publisher.publish_event(
        event_type="user.activated",
        user_id=admin_id,
        data={
            "target_user_id": target_user_id
        }
    )

