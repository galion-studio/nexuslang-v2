"""
AI Clock System for Galion Ecosystem
Internal timing and monitoring system for all AI operations
Tracks performance, costs, and usage across all AI interactions
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import statistics
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class AIClockEvent:
    """Represents a single AI operation event"""

    def __init__(
        self,
        operation_id: str,
        operation_type: str,
        model_name: str,
        provider: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        platform: str = "unknown"
    ):
        self.operation_id = operation_id
        self.operation_type = operation_type  # summary, generation, chat, etc.
        self.model_name = model_name
        self.provider = provider
        self.user_id = user_id
        self.session_id = session_id
        self.platform = platform  # galion_studio, galion_app, developer_platform

        # Timing
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None

        # Performance metrics
        self.tokens_input = 0
        self.tokens_output = 0
        self.tokens_total = 0
        self.cost_usd = 0.0
        self.success = False

        # Context
        self.input_length = 0
        self.output_length = 0
        self.parameters: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

        # Error tracking
        self.error_type: Optional[str] = None
        self.error_message: Optional[str] = None

    def complete(self, success: bool = True, error_type: str = None, error_message: str = None):
        """Mark the operation as completed"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success

        if not success:
            self.error_type = error_type
            self.error_message = error_message

        self.tokens_total = self.tokens_input + self.tokens_output

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            'operation_id': self.operation_id,
            'operation_type': self.operation_type,
            'model_name': self.model_name,
            'provider': self.provider,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'platform': self.platform,
            'timestamp': datetime.fromtimestamp(self.start_time).isoformat(),
            'duration_seconds': round(self.duration, 3) if self.duration else None,
            'tokens_input': self.tokens_input,
            'tokens_output': self.tokens_output,
            'tokens_total': self.tokens_total,
            'cost_usd': self.cost_usd,
            'success': self.success,
            'input_length': self.input_length,
            'output_length': self.output_length,
            'parameters': self.parameters,
            'metadata': self.metadata,
            'error_type': self.error_type,
            'error_message': self.error_message
        }


class AIClockMetrics:
    """Real-time AI performance metrics"""

    def __init__(self):
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.total_duration = 0.0
        self.total_cost = 0.0
        self.total_tokens = 0

        # Rolling averages (last 1000 operations)
        self.recent_durations = deque(maxlen=1000)
        self.recent_latencies = deque(maxlen=1000)

        # Per-model metrics
        self.model_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'operations': 0,
            'successful': 0,
            'total_duration': 0.0,
            'total_cost': 0.0,
            'total_tokens': 0,
            'avg_duration': 0.0,
            'avg_cost': 0.0,
            'success_rate': 0.0
        })

        # Per-provider metrics
        self.provider_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'operations': 0,
            'successful': 0,
            'total_duration': 0.0,
            'total_cost': 0.0,
            'total_tokens': 0,
            'avg_duration': 0.0,
            'avg_cost': 0.0,
            'success_rate': 0.0
        })

        # Per-platform metrics
        self.platform_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'operations': 0,
            'successful': 0,
            'total_duration': 0.0,
            'total_cost': 0.0,
            'total_tokens': 0
        })

    def record_event(self, event: AIClockEvent):
        """Record an AI operation event"""
        self.total_operations += 1

        if event.success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1

        if event.duration:
            self.total_duration += event.duration
            self.recent_durations.append(event.duration)

        self.total_cost += event.cost_usd
        self.total_tokens += event.tokens_total

        # Update model metrics
        model_stats = self.model_metrics[event.model_name]
        model_stats['operations'] += 1
        if event.success:
            model_stats['successful'] += 1
        if event.duration:
            model_stats['total_duration'] += event.duration
        model_stats['total_cost'] += event.cost_usd
        model_stats['total_tokens'] += event.tokens_total

        # Update provider metrics
        provider_stats = self.provider_metrics[event.provider]
        provider_stats['operations'] += 1
        if event.success:
            provider_stats['successful'] += 1
        if event.duration:
            provider_stats['total_duration'] += event.duration
        provider_stats['total_cost'] += event.cost_usd
        provider_stats['total_tokens'] += event.tokens_total

        # Update platform metrics
        platform_stats = self.platform_metrics[event.platform]
        platform_stats['operations'] += 1
        if event.success:
            platform_stats['successful'] += 1
        if event.duration:
            platform_stats['total_duration'] += event.duration
        platform_stats['total_cost'] += event.cost_usd
        platform_stats['total_tokens'] += event.tokens_total

        # Calculate rolling averages
        self._update_averages()

    def _update_averages(self):
        """Update average calculations"""
        # Overall success rate
        if self.total_operations > 0:
            success_rate = self.successful_operations / self.total_operations

        # Model averages
        for model, stats in self.model_metrics.items():
            if stats['operations'] > 0:
                stats['avg_duration'] = stats['total_duration'] / stats['operations']
                stats['avg_cost'] = stats['total_cost'] / stats['operations']
                stats['success_rate'] = stats['successful'] / stats['operations']

        # Provider averages
        for provider, stats in self.provider_metrics.items():
            if stats['operations'] > 0:
                stats['avg_duration'] = stats['total_duration'] / stats['operations']
                stats['avg_cost'] = stats['total_cost'] / stats['operations']
                stats['success_rate'] = stats['successful'] / stats['operations']

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        avg_duration = self.total_duration / self.total_operations if self.total_operations > 0 else 0
        avg_cost = self.total_cost / self.total_operations if self.total_operations > 0 else 0
        success_rate = self.successful_operations / self.total_operations if self.total_operations > 0 else 0

        # Calculate percentiles for recent operations
        duration_percentiles = {}
        if self.recent_durations:
            durations_sorted = sorted(self.recent_durations)
            duration_percentiles = {
                'p50': durations_sorted[int(len(durations_sorted) * 0.5)],
                'p95': durations_sorted[int(len(durations_sorted) * 0.95)],
                'p99': durations_sorted[int(len(durations_sorted) * 0.99)]
            }

        return {
            'overall': {
                'total_operations': self.total_operations,
                'successful_operations': self.successful_operations,
                'failed_operations': self.failed_operations,
                'success_rate': round(success_rate, 3),
                'avg_duration_seconds': round(avg_duration, 3),
                'avg_cost_usd': round(avg_cost, 4),
                'total_cost_usd': round(self.total_cost, 2),
                'total_tokens': self.total_tokens,
                'duration_percentiles': {k: round(v, 3) for k, v in duration_percentiles.items()}
            },
            'by_model': dict(self.model_metrics),
            'by_provider': dict(self.provider_metrics),
            'by_platform': dict(self.platform_metrics),
            'timestamp': datetime.now().isoformat()
        }


class AIClock:
    """Main AI Clock system for tracking all AI operations"""

    def __init__(self):
        self.metrics = AIClockMetrics()
        self.active_operations: Dict[str, AIClockEvent] = {}
        self.event_handlers: List[Callable] = []
        self.storage_enabled = True
        self.storage_buffer: List[AIClockEvent] = []
        self.storage_batch_size = 100

    def add_event_handler(self, handler: Callable):
        """Add an event handler for AI operation events"""
        self.event_handlers.append(handler)

    def remove_event_handler(self, handler: Callable):
        """Remove an event handler"""
        self.event_handlers.remove(handler)

    @asynccontextmanager
    async def track_operation(
        self,
        operation_type: str,
        model_name: str,
        provider: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        platform: str = "unknown"
    ):
        """Context manager for tracking AI operations"""
        operation_id = f"{operation_type}_{model_name}_{int(time.time() * 1000000)}"

        event = AIClockEvent(
            operation_id=operation_id,
            operation_type=operation_type,
            model_name=model_name,
            provider=provider,
            user_id=user_id,
            session_id=session_id,
            platform=platform
        )

        self.active_operations[operation_id] = event

        try:
            yield event
            event.complete(success=True)
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            event.complete(success=False, error_type=error_type, error_message=error_message)
            raise
        finally:
            # Record metrics
            self.metrics.record_event(event)

            # Trigger event handlers
            for handler in self.event_handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed: {e}")

            # Clean up
            del self.active_operations[operation_id]

            # Store event if enabled
            if self.storage_enabled:
                self.storage_buffer.append(event)
                if len(self.storage_buffer) >= self.storage_batch_size:
                    await self._flush_storage_buffer()

    async def _flush_storage_buffer(self):
        """Flush buffered events to storage"""
        if not self.storage_buffer:
            return

        try:
            # In a real implementation, this would save to database/cache
            # For now, just log the events
            for event in self.storage_buffer:
                logger.info(f"AI Operation: {event.to_dict()}")

            self.storage_buffer.clear()

        except Exception as e:
            logger.error(f"Failed to flush AI clock buffer: {e}")

    def get_operation_status(self, operation_id: str) -> Optional[AIClockEvent]:
        """Get the status of an active operation"""
        return self.active_operations.get(operation_id)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        return self.metrics.get_summary()

    def get_active_operations(self) -> Dict[str, AIClockEvent]:
        """Get all currently active operations"""
        return dict(self.active_operations)

    def get_operation_stats(self, operation_type: str = None, model_name: str = None,
                           provider: str = None, platform: str = None,
                           hours: int = 24) -> Dict[str, Any]:
        """Get statistics for specific operation filters"""
        # In a real implementation, this would query stored events
        # For now, return current metrics summary
        return self.get_metrics_summary()

    async def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        summary = self.get_metrics_summary()

        if format == "json":
            return json.dumps(summary, indent=2, default=str)
        elif format == "csv":
            # Simplified CSV export
            lines = ["Metric,Value"]
            for category, data in summary.items():
                if isinstance(data, dict):
                    for key, value in data.items():
                        lines.append(f"{category}.{key},{value}")
                else:
                    lines.append(f"{category},{data}")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global AI Clock instance
_ai_clock: Optional[AIClock] = None

def get_ai_clock() -> AIClock:
    """Get global AI clock instance"""
    global _ai_clock
    if _ai_clock is None:
        _ai_clock = AIClock()

        # Add default event handler for logging
        async def log_handler(event: AIClockEvent):
            level = logging.INFO if event.success else logging.WARNING
            logger.log(level, f"AI Operation: {event.operation_type} on {event.model_name} "
                            f"({event.duration:.3f}s, ${event.cost_usd:.4f}, {event.success})")

        _ai_clock.add_event_handler(log_handler)

    return _ai_clock


# Convenience functions for common AI operations
@asynccontextmanager
async def track_ai_operation(operation_type: str, model_name: str, provider: str, **kwargs):
    """Convenience context manager for tracking AI operations"""
    ai_clock = get_ai_clock()
    async with ai_clock.track_operation(operation_type, model_name, provider, **kwargs) as event:
        yield event


async def track_text_generation(model_name: str, provider: str, input_tokens: int,
                               output_tokens: int, cost: float, **kwargs):
    """Track text generation operation"""
    ai_clock = get_ai_clock()
    async with ai_clock.track_operation("text_generation", model_name, provider, **kwargs) as event:
        event.tokens_input = input_tokens
        event.tokens_output = output_tokens
        event.cost_usd = cost
        event.input_length = input_tokens
        event.output_length = output_tokens
        yield event


async def track_image_generation(model_name: str, provider: str, cost: float,
                                resolution: str = None, **kwargs):
    """Track image generation operation"""
    ai_clock = get_ai_clock()
    async with ai_clock.track_operation("image_generation", model_name, provider, **kwargs) as event:
        event.cost_usd = cost
        event.parameters = {"resolution": resolution}
        yield event


async def track_embedding_generation(model_name: str, provider: str, input_tokens: int,
                                    cost: float, **kwargs):
    """Track embedding generation operation"""
    ai_clock = get_ai_clock()
    async with ai_clock.track_operation("embedding", model_name, provider, **kwargs) as event:
        event.tokens_input = input_tokens
        event.cost_usd = cost
        event.input_length = input_tokens
        yield event


async def track_chat_completion(model_name: str, provider: str, input_tokens: int,
                               output_tokens: int, cost: float, **kwargs):
    """Track chat completion operation"""
    ai_clock = get_ai_clock()
    async with ai_clock.track_operation("chat", model_name, provider, **kwargs) as event:
        event.tokens_input = input_tokens
        event.tokens_output = output_tokens
        event.cost_usd = cost
        event.input_length = input_tokens
        event.output_length = output_tokens
        yield event


# Monitoring and alerting functions
async def check_ai_performance_alerts() -> List[str]:
    """Check for AI performance alerts"""
    ai_clock = get_ai_clock()
    summary = ai_clock.get_metrics_summary()
    alerts = []

    overall = summary.get('overall', {})

    # Check success rate
    success_rate = overall.get('success_rate', 1.0)
    if success_rate < 0.95:
        alerts.append(".1%")

    # Check average duration
    avg_duration = overall.get('avg_duration_seconds', 0)
    if avg_duration > 30:  # 30 seconds
        alerts.append(f"High average AI response time: {avg_duration:.1f}s")

    # Check cost efficiency
    total_ops = overall.get('total_operations', 0)
    total_cost = overall.get('total_cost_usd', 0)
    if total_ops > 100 and total_cost / total_ops > 0.01:  # $0.01 per operation
        alerts.append(".4f")

    return alerts


# Cost tracking utilities
def calculate_operation_cost(model_name: str, provider: str, input_tokens: int = 0,
                           output_tokens: int = 0, **kwargs) -> float:
    """Calculate cost for an AI operation based on pricing"""
    # Simplified pricing model - in production, this would be more sophisticated
    pricing = {
        'gpt-4': {'input': 0.03, 'output': 0.06},  # per 1K tokens
        'gpt-3.5-turbo': {'input': 0.002, 'output': 0.002},
        'claude-3': {'input': 0.015, 'output': 0.075},
        'dall-e-3': {'cost': 0.08},  # per image
        'stable-diffusion': {'cost': 0.02},  # per image
    }

    model_pricing = pricing.get(model_name.lower(), {'input': 0.001, 'output': 0.002})

    if 'cost' in model_pricing:
        # Fixed cost per operation
        return model_pricing['cost']
    else:
        # Token-based pricing
        input_cost = (input_tokens / 1000) * model_pricing['input']
        output_cost = (output_tokens / 1000) * model_pricing['output']
        return input_cost + output_cost


# Performance monitoring utilities
def get_ai_performance_score() -> float:
    """Calculate overall AI performance score (0-100)"""
    ai_clock = get_ai_clock()
    summary = ai_clock.get_metrics_summary()
    overall = summary.get('overall', {})

    score = 100.0

    # Penalize for low success rate
    success_rate = overall.get('success_rate', 1.0)
    if success_rate < 0.95:
        score -= (1 - success_rate) * 500  # Max 25 point penalty

    # Penalize for slow responses
    avg_duration = overall.get('avg_duration_seconds', 0)
    if avg_duration > 10:
        score -= min(25, (avg_duration - 10) / 2)  # Max 25 point penalty

    # Penalize for high costs
    total_ops = overall.get('total_operations', 0)
    if total_ops > 100:
        avg_cost = overall.get('avg_cost_usd', 0)
        if avg_cost > 0.005:  # $0.005 per operation
            score -= min(20, (avg_cost - 0.005) * 4000)  # Max 20 point penalty

    return max(0.0, min(100.0, score))
