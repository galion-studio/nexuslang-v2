"""
Kafka event producer for document events
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "user-events")

class DocumentEventProducer:
    """Kafka producer for document events"""
    
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
            self.connected = True
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}")
            self.connected = False
            self.producer = None
    
    def publish_event(self, event_type: str, user_id: str, data: Dict[str, Any]) -> bool:
        """
        Publish event to Kafka
        
        Args:
            event_type: Type of event (e.g., 'document.uploaded')
            user_id: User ID
            data: Event data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.producer:
            print("Kafka producer not connected")
            return False
        
        event = {
            "event_type": event_type,
            "user_id": str(user_id),
            "service": "document-service",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data
        }
        
        try:
            future = self.producer.send(KAFKA_TOPIC, value=event)
            future.get(timeout=10)  # Wait for confirmation
            return True
        except KafkaError as e:
            print(f"Failed to publish event: {e}")
            return False
    
    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()

# Singleton instance
kafka_producer = DocumentEventProducer()

