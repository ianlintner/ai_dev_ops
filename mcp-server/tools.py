"""
MCP Observability Server Tools

This module implements the MCP tools for querying observability data.
Each tool provides specific functionality for AI agents to investigate
incidents, search logs, query traces, and analyze metrics.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TimeRange:
    """Represents a time range for queries."""
    start: datetime
    end: datetime
    
    @classmethod
    def from_string(cls, range_str: str) -> "TimeRange":
        """
        Parse time range from string.
        
        Supported formats:
        - "last_5m", "last_15m", "last_hour", "last_24h", "last_7d"
        - ISO 8601 datetime ranges
        """
        now = datetime.utcnow()
        
        range_map = {
            "last_5m": timedelta(minutes=5),
            "last_15m": timedelta(minutes=15),
            "last_30m": timedelta(minutes=30),
            "last_hour": timedelta(hours=1),
            "last_3h": timedelta(hours=3),
            "last_6h": timedelta(hours=6),
            "last_12h": timedelta(hours=12),
            "last_24h": timedelta(hours=24),
            "last_7d": timedelta(days=7),
            "last_30d": timedelta(days=30),
        }
        
        if range_str in range_map:
            delta = range_map[range_str]
            return cls(start=now - delta, end=now)
        
        # Default to last hour if unknown
        return cls(start=now - timedelta(hours=1), end=now)


class SearchLogsToolparameters
    """
    Tool for searching log entries.
    
    Provides full-text search and semantic similarity search across logs.
    """
    
    def __init__(self, data_store):
        """
        Initialize the search logs tool.
        
        Args:
            data_store: Data store instance for querying logs
        """
        self.data_store = data_store
    
    def execute(
        self,
        query: str,
        service_name: Optional[str] = None,
        time_range: str = "last_hour",
        severity: Optional[str] = None,
        limit: int = 10,
        use_semantic: bool = False,
    ) -> Dict[str, Any]:
        """
        Search log entries.
        
        Args:
            query: Search query (full-text or natural language)
            service_name: Filter by service name
            time_range: Time range for search
            severity: Filter by severity (debug, info, warning, error, critical)
            limit: Maximum number of results
            use_semantic: Use semantic similarity search
            
        Returns:
            Dictionary with search results and metadata
        """
        time_window = TimeRange.from_string(time_range)
        
        logger.info(
            f"Searching logs: query='{query}', service={service_name}, "
            f"time_range={time_range}, severity={severity}"
        )
        
        # Build query filters
        filters = {
            "time_range": {"start": time_window.start, "end": time_window.end},
        }
        
        if service_name:
            filters["service_name"] = service_name
        if severity:
            filters["severity"] = severity
        
        # Execute search
        results = self.data_store.search_logs(
            query=query,
            filters=filters,
            limit=limit,
            use_semantic=use_semantic,
        )
        
        return {
            "status": "success",
            "results": results,
            "metadata": {
                "count": len(results),
                "query": query,
                "time_range": time_range,
                "filters": filters,
            },
        }


class QueryTracesTool:
    """
    Tool for querying distributed traces.
    
    Finds traces matching various criteria including service, operation,
    duration, and error status.
    """
    
    def __init__(self, data_store):
        """
        Initialize the query traces tool.
        
        Args:
            data_store: Data store instance for querying traces
        """
        self.data_store = data_store
    
    def execute(
        self,
        trace_id: Optional[str] = None,
        service_name: Optional[str] = None,
        operation: Optional[str] = None,
        min_duration_ms: Optional[int] = None,
        has_error: Optional[bool] = None,
        time_range: str = "last_hour",
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Query distributed traces.
        
        Args:
            trace_id: Specific trace ID to retrieve
            service_name: Filter by service name
            operation: Filter by operation name
            min_duration_ms: Minimum duration in milliseconds
            has_error: Filter traces with errors
            time_range: Time range for query
            limit: Maximum number of results
            
        Returns:
            Dictionary with trace results and metadata
        """
        time_window = TimeRange.from_string(time_range)
        
        logger.info(
            f"Querying traces: trace_id={trace_id}, service={service_name}, "
            f"operation={operation}, time_range={time_range}"
        )
        
        # Build query filters
        filters = {
            "time_range": {"start": time_window.start, "end": time_window.end},
        }
        
        if trace_id:
            filters["trace_id"] = trace_id
        if service_name:
            filters["service_name"] = service_name
        if operation:
            filters["operation"] = operation
        if min_duration_ms:
            filters["min_duration_ms"] = min_duration_ms
        if has_error is not None:
            filters["has_error"] = has_error
        
        # Execute query
        results = self.data_store.query_traces(filters=filters, limit=limit)
        
        return {
            "status": "success",
            "results": results,
            "metadata": {
                "count": len(results),
                "time_range": time_range,
                "filters": filters,
            },
        }


class GetMetricsTool:
    """
    Tool for retrieving time-series metrics.
    
    Supports various aggregations and grouping dimensions.
    """
    
    def __init__(self, data_store):
        """
        Initialize the get metrics tool.
        
        Args:
            data_store: Data store instance for querying metrics
        """
        self.data_store = data_store
    
    def execute(
        self,
        metric_name: str,
        aggregation: str = "avg",
        time_range: str = "last_hour",
        labels: Optional[Dict[str, str]] = None,
        group_by: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get time-series metrics.
        
        Args:
            metric_name: Name of the metric
            aggregation: Aggregation type (avg, sum, min, max, p50, p95, p99)
            time_range: Time range for metrics
            labels: Label filters (key-value pairs)
            group_by: Dimensions to group by
            
        Returns:
            Dictionary with metric data and metadata
        """
        time_window = TimeRange.from_string(time_range)
        
        logger.info(
            f"Getting metrics: metric={metric_name}, agg={aggregation}, "
            f"time_range={time_range}"
        )
        
        # Execute query
        results = self.data_store.get_metrics(
            metric_name=metric_name,
            aggregation=aggregation,
            time_range={"start": time_window.start, "end": time_window.end},
            labels=labels or {},
            group_by=group_by or [],
        )
        
        return {
            "status": "success",
            "results": results,
            "metadata": {
                "metric_name": metric_name,
                "aggregation": aggregation,
                "time_range": time_range,
                "labels": labels,
                "group_by": group_by,
            },
        }


class CorrelateEventsTool:
    """
    Tool for correlating events across all telemetry types.
    
    Finds all related traces, logs, metrics, and events for a correlation ID.
    """
    
    def __init__(self, data_store):
        """
        Initialize the correlate events tool.
        
        Args:
            data_store: Data store instance for correlating events
        """
        self.data_store = data_store
    
    def execute(
        self,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
        include_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Correlate events across telemetry types.
        
        Args:
            correlation_id: Correlation ID
            trace_id: Trace ID
            request_id: Request ID
            include_types: Types to include (traces, logs, metrics, events)
            
        Returns:
            Dictionary with correlated telemetry
        """
        if not correlation_id and not trace_id and not request_id:
            return {
                "status": "error",
                "error": "At least one of correlation_id, trace_id, or request_id is required",
            }
        
        logger.info(
            f"Correlating events: correlation_id={correlation_id}, "
            f"trace_id={trace_id}, request_id={request_id}"
        )
        
        # Build query
        query = {}
        if correlation_id:
            query["correlation_id"] = correlation_id
        if trace_id:
            query["trace_id"] = trace_id
        if request_id:
            query["request_id"] = request_id
        
        # Set default types if not specified
        if include_types is None:
            include_types = ["traces", "logs", "metrics", "events"]
        
        # Execute correlation
        results = self.data_store.correlate_events(
            query=query, include_types=include_types
        )
        
        return {
            "status": "success",
            "results": results,
            "metadata": {
                "correlation_id": correlation_id,
                "trace_id": trace_id,
                "request_id": request_id,
                "types_included": include_types,
            },
        }


class AnalyzeIncidentTool:
    """
    Tool for AI-powered incident analysis.
    
    Performs root cause analysis using ML and historical incident data.
    """
    
    def __init__(self, data_store, analyzer):
        """
        Initialize the analyze incident tool.
        
        Args:
            data_store: Data store instance
            analyzer: Incident analyzer instance
        """
        self.data_store = data_store
        self.analyzer = analyzer
    
    def execute(
        self,
        incident_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        time_range: str = "last_hour",
        affected_services: Optional[List[str]] = None,
        symptoms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze incident and provide root cause analysis.
        
        Args:
            incident_id: Incident ID
            correlation_id: Correlation ID
            time_range: Time range to analyze
            affected_services: List of affected services
            symptoms: List of observed symptoms
            
        Returns:
            Dictionary with analysis results
        """
        time_window = TimeRange.from_string(time_range)
        
        logger.info(
            f"Analyzing incident: incident_id={incident_id}, "
            f"services={affected_services}, symptoms={symptoms}"
        )
        
        # Gather relevant telemetry
        telemetry = self._gather_telemetry(
            correlation_id=correlation_id,
            time_window=time_window,
            services=affected_services or [],
        )
        
        # Perform analysis
        analysis = self.analyzer.analyze(
            telemetry=telemetry,
            symptoms=symptoms or [],
            services=affected_services or [],
        )
        
        return {
            "status": "success",
            "analysis": analysis,
            "metadata": {
                "incident_id": incident_id,
                "time_range": time_range,
                "affected_services": affected_services,
                "telemetry_count": len(telemetry),
            },
        }
    
    def _gather_telemetry(
        self,
        correlation_id: Optional[str],
        time_window: TimeRange,
        services: List[str],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Gather all relevant telemetry for analysis."""
        telemetry = {
            "traces": [],
            "logs": [],
            "metrics": [],
            "events": [],
        }
        
        # Gather traces
        trace_filters = {
            "time_range": {"start": time_window.start, "end": time_window.end},
        }
        if correlation_id:
            trace_filters["correlation_id"] = correlation_id
        if services:
            trace_filters["service_name"] = services
        
        telemetry["traces"] = self.data_store.query_traces(
            filters=trace_filters, limit=100
        )
        
        # Gather logs
        log_filters = {
            "time_range": {"start": time_window.start, "end": time_window.end},
            "severity": ["error", "critical"],
        }
        if services:
            log_filters["service_name"] = services
        
        telemetry["logs"] = self.data_store.search_logs(
            query="*", filters=log_filters, limit=100
        )
        
        return telemetry


# Tool registry
TOOLS = {
    "search_logs": {
        "name": "search_logs",
        "description": "Search log entries with full-text or semantic search",
        "parameters": {
            "query": {"type": "string", "required": True},
            "service_name": {"type": "string", "required": False},
            "time_range": {"type": "string", "default": "last_hour"},
            "severity": {"type": "string", "required": False},
            "limit": {"type": "integer", "default": 10},
        },
    },
    "query_traces": {
        "name": "query_traces",
        "description": "Query distributed traces by various criteria",
        "parameters": {
            "trace_id": {"type": "string", "required": False},
            "service_name": {"type": "string", "required": False},
            "operation": {"type": "string", "required": False},
            "min_duration_ms": {"type": "integer", "required": False},
            "time_range": {"type": "string", "default": "last_hour"},
            "limit": {"type": "integer", "default": 20},
        },
    },
    "get_metrics": {
        "name": "get_metrics",
        "description": "Retrieve time-series metrics with aggregations",
        "parameters": {
            "metric_name": {"type": "string", "required": True},
            "aggregation": {"type": "string", "default": "avg"},
            "time_range": {"type": "string", "default": "last_hour"},
            "labels": {"type": "object", "required": False},
        },
    },
    "correlate_events": {
        "name": "correlate_events",
        "description": "Find all related telemetry for a correlation ID",
        "parameters": {
            "correlation_id": {"type": "string", "required": False},
            "trace_id": {"type": "string", "required": False},
            "request_id": {"type": "string", "required": False},
            "include_types": {"type": "array", "required": False},
        },
    },
    "analyze_incident": {
        "name": "analyze_incident",
        "description": "AI-powered root cause analysis for incidents",
        "parameters": {
            "time_range": {"type": "string", "default": "last_hour"},
            "affected_services": {"type": "array", "required": False},
            "symptoms": {"type": "array", "required": False},
        },
    },
}
