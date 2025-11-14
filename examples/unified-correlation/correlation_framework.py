"""
Unified Correlation Framework

This module provides utilities for correlating traces, logs, metrics, and events
in a distributed system. It implements the unified correlation schema and provides
middleware for automatic correlation ID propagation.

Key Features:
- Automatic correlation ID generation and propagation
- Context-aware correlation across services
- Unified telemetry linking
- Support for OpenTelemetry, logs, metrics, and custom events
"""

import hashlib
import json
import logging
import os
import time
import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Context variable to store correlation context across async boundaries
_correlation_context: ContextVar[Optional["CorrelationContext"]] = ContextVar(
    "correlation_context", default=None
)


@dataclass
class CorrelationContext:
    """
    Context for unified correlation across all telemetry types.
    
    This class maintains the correlation state throughout a request's
    lifecycle and across service boundaries.
    """
    
    correlation_id: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    service_name: str = "unknown"
    environment: str = "development"
    cluster: Optional[str] = None
    namespace: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    related_traces: List[str] = field(default_factory=list)
    related_logs: List[str] = field(default_factory=list)
    related_metrics: List[str] = field(default_factory=list)
    related_events: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def to_log_extra(self) -> Dict[str, Any]:
        """Convert context to logging extra fields."""
        return {
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "service_name": self.service_name,
            "environment": self.environment,
        }
    
    def to_http_headers(self) -> Dict[str, str]:
        """Convert context to HTTP headers for propagation."""
        headers = {
            "X-Correlation-ID": self.correlation_id,
        }
        if self.trace_id:
            headers["X-Trace-ID"] = self.trace_id
        if self.request_id:
            headers["X-Request-ID"] = self.request_id
        if self.user_id:
            headers["X-User-ID"] = self.user_id
        if self.session_id:
            headers["X-Session-ID"] = self.session_id
        return headers


class CorrelationManager:
    """
    Manager for creating and managing correlation contexts.
    
    Provides utilities for:
    - Generating correlation IDs
    - Managing correlation context
    - Propagating correlation across services
    - Linking telemetry signals
    """
    
    def __init__(
        self,
        service_name: str = None,
        environment: str = None,
        cluster: str = None,
        namespace: str = None,
    ):
        self.service_name = service_name or os.getenv("SERVICE_NAME", "unknown")
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.cluster = cluster or os.getenv("CLUSTER_NAME")
        self.namespace = namespace or os.getenv("NAMESPACE")
        self.tracer = trace.get_tracer(__name__)
    
    @staticmethod
    def generate_correlation_id() -> str:
        """Generate a unique correlation ID."""
        return uuid.uuid4().hex
    
    @staticmethod
    def hash_user_id(user_id: str) -> str:
        """Hash user ID for privacy."""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def create_context(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> CorrelationContext:
        """
        Create a new correlation context.
        
        Args:
            request_id: HTTP request ID or transaction ID
            user_id: User identifier (will be hashed)
            session_id: Session identifier
            tenant_id: Tenant identifier for multi-tenant systems
            correlation_id: Existing correlation ID (or generate new one)
            tags: Additional tags for categorization
            
        Returns:
            CorrelationContext instance
        """
        # Get current trace context
        current_span = trace.get_current_span()
        trace_id = None
        span_id = None
        
        if current_span and current_span.get_span_context().is_valid:
            span_context = current_span.get_span_context()
            trace_id = format(span_context.trace_id, "032x")
            span_id = format(span_context.span_id, "016x")
        
        # Hash user ID for privacy
        hashed_user_id = None
        if user_id:
            hashed_user_id = f"usr_hash_{self.hash_user_id(user_id)}"
        
        context = CorrelationContext(
            correlation_id=correlation_id or self.generate_correlation_id(),
            trace_id=trace_id,
            span_id=span_id,
            request_id=request_id,
            user_id=hashed_user_id,
            session_id=session_id,
            tenant_id=tenant_id,
            service_name=self.service_name,
            environment=self.environment,
            cluster=self.cluster,
            namespace=self.namespace,
            tags=tags or {},
        )
        
        # Store in context var
        _correlation_context.set(context)
        
        return context
    
    @staticmethod
    def get_context() -> Optional[CorrelationContext]:
        """Get the current correlation context."""
        return _correlation_context.get()
    
    @staticmethod
    def from_http_headers(headers: Dict[str, str]) -> Optional[CorrelationContext]:
        """
        Extract correlation context from HTTP headers.
        
        Args:
            headers: HTTP headers dictionary
            
        Returns:
            CorrelationContext if found in headers, None otherwise
        """
        correlation_id = headers.get("X-Correlation-ID")
        if not correlation_id:
            return None
        
        context = CorrelationContext(
            correlation_id=correlation_id,
            trace_id=headers.get("X-Trace-ID"),
            request_id=headers.get("X-Request-ID"),
            user_id=headers.get("X-User-ID"),
            session_id=headers.get("X-Session-ID"),
        )
        
        _correlation_context.set(context)
        return context
    
    def link_trace(self, trace_id: str):
        """Link a trace to the current correlation context."""
        context = self.get_context()
        if context and trace_id not in context.related_traces:
            context.related_traces.append(trace_id)
    
    def link_log(self, log_id: str):
        """Link a log entry to the current correlation context."""
        context = self.get_context()
        if context and log_id not in context.related_logs:
            context.related_logs.append(log_id)
    
    def link_metric(self, metric_name: str):
        """Link a metric to the current correlation context."""
        context = self.get_context()
        if context and metric_name not in context.related_metrics:
            context.related_metrics.append(metric_name)
    
    def link_event(self, event_id: str):
        """Link an event to the current correlation context."""
        context = self.get_context()
        if context and event_id not in context.related_events:
            context.related_events.append(event_id)


class CorrelatedLogger:
    """
    Logger that automatically includes correlation context in all log entries.
    """
    
    def __init__(self, name: str, manager: CorrelationManager):
        self.logger = logging.getLogger(name)
        self.manager = manager
    
    def _log_with_context(
        self, level: int, msg: str, *args, extra: Optional[Dict] = None, **kwargs
    ):
        """Log with correlation context."""
        context = self.manager.get_context()
        log_extra = extra or {}
        
        if context:
            log_extra.update(context.to_log_extra())
            # Generate log ID and link it
            log_id = f"log_{uuid.uuid4().hex[:12]}"
            log_extra["log_id"] = log_id
            self.manager.link_log(log_id)
        
        self.logger.log(level, msg, *args, extra=log_extra, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        """Log debug message with correlation."""
        self._log_with_context(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log info message with correlation."""
        self._log_with_context(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log warning message with correlation."""
        self._log_with_context(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log error message with correlation."""
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log critical message with correlation."""
        self._log_with_context(logging.CRITICAL, msg, *args, **kwargs)


class CorrelatedTracer:
    """
    Wrapper around OpenTelemetry tracer that automatically adds correlation context.
    """
    
    def __init__(self, manager: CorrelationManager):
        self.manager = manager
        self.tracer = trace.get_tracer(__name__)
    
    def start_span(self, name: str, **kwargs):
        """
        Start a span with automatic correlation context attributes.
        
        Args:
            name: Span name
            **kwargs: Additional arguments for start_as_current_span
            
        Returns:
            Context manager for the span
        """
        context = self.manager.get_context()
        
        # Create span
        span = self.tracer.start_as_current_span(name, **kwargs)
        
        # Add correlation attributes
        if context:
            with span as s:
                s.set_attribute("correlation.id", context.correlation_id)
                s.set_attribute("service.name", context.service_name)
                s.set_attribute("service.environment", context.environment)
                if context.request_id:
                    s.set_attribute("request.id", context.request_id)
                if context.user_id:
                    s.set_attribute("user.id", context.user_id)
                if context.cluster:
                    s.set_attribute("k8s.cluster.name", context.cluster)
                if context.namespace:
                    s.set_attribute("k8s.namespace.name", context.namespace)
                
                # Add custom tags
                for key, value in context.tags.items():
                    s.set_attribute(f"tag.{key}", value)
                
                # Link trace ID
                span_context = s.get_span_context()
                if span_context.is_valid:
                    trace_id = format(span_context.trace_id, "032x")
                    self.manager.link_trace(trace_id)
        
        return span


def setup_correlation(
    service_name: str = None,
    environment: str = None,
    cluster: str = None,
    namespace: str = None,
) -> CorrelationManager:
    """
    Set up correlation framework for the application.
    
    Args:
        service_name: Name of the service
        environment: Environment (production, staging, etc.)
        cluster: Kubernetes cluster name
        namespace: Kubernetes namespace
        
    Returns:
        CorrelationManager instance
    """
    manager = CorrelationManager(
        service_name=service_name,
        environment=environment,
        cluster=cluster,
        namespace=namespace,
    )
    return manager


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Set up correlation
    manager = setup_correlation(
        service_name="payment-service",
        environment="production",
        cluster="us-west-2-prod",
        namespace="payment-services",
    )
    
    # Create logger and tracer
    logger = CorrelatedLogger("payment", manager)
    tracer = CorrelatedTracer(manager)
    
    # Create correlation context for a request
    context = manager.create_context(
        request_id="req_123456",
        user_id="user_789",
        tags={"team": "payments", "component": "processor"},
    )
    
    print(f"\nCreated correlation context:")
    print(json.dumps(context.to_dict(), indent=2))
    
    # Use correlated tracing and logging
    with tracer.start_span("process_payment"):
        logger.info("Starting payment processing", extra={"amount": 99.99})
        
        # Simulate work
        time.sleep(0.1)
        
        with tracer.start_span("validate_payment"):
            logger.info("Validating payment details")
            time.sleep(0.05)
        
        with tracer.start_span("charge_card"):
            logger.info("Charging credit card")
            time.sleep(0.1)
        
        logger.info("Payment completed successfully")
    
    # Print correlation context with linked telemetry
    final_context = manager.get_context()
    print(f"\nFinal correlation context with linked telemetry:")
    print(json.dumps(final_context.to_dict(), indent=2))
    
    # Show HTTP headers for propagation
    print(f"\nHTTP headers for propagation:")
    print(json.dumps(final_context.to_http_headers(), indent=2))
