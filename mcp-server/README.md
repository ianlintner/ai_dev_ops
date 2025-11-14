# MCP Observability Server

Model Context Protocol (MCP) server that exposes observability data through standardized tools for AI agents.

## Overview

This MCP server provides AI agents with tools to query traces, logs, metrics, and events from your observability infrastructure. It enables natural language queries and automated incident investigation.

## Features

- **Search Logs**: Full-text and semantic search across log entries
- **Query Traces**: Find distributed traces by various criteria
- **Get Metrics**: Retrieve time-series metrics data
- **Correlate Events**: Find all related telemetry across signal types
- **Analyze Incidents**: AI-powered root cause analysis

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set environment variables:

```bash
export OTEL_ENDPOINT="http://localhost:4317"
export ELASTICSEARCH_URL="http://localhost:9200"
export TIMESCALEDB_URL="postgresql://user:pass@localhost:5432/metrics"
export CHROMADB_PATH="./chroma_data"
export REDIS_URL="redis://localhost:6379/0"
```

## Usage

### Start the Server

```bash
python server.py
```

### Using with AI Agents

The server exposes MCP tools that AI agents can call:

```python
# Example: AI agent searching for errors
result = mcp_client.call_tool(
    "search_logs",
    query="payment failed",
    time_range="last_hour",
    severity="error"
)
```

## Available Tools

### search_logs

Search log entries with filtering and semantic similarity.

**Parameters:**
- `query` (string): Search query or natural language question
- `service_name` (string, optional): Filter by service
- `time_range` (string): Time range (e.g., "last_hour", "last_24h")
- `severity` (string, optional): Filter by severity level
- `limit` (integer): Maximum results to return

### query_traces

Find distributed traces matching criteria.

**Parameters:**
- `trace_id` (string, optional): Specific trace ID
- `service_name` (string, optional): Filter by service
- `operation` (string, optional): Filter by operation name
- `min_duration_ms` (integer, optional): Minimum duration
- `time_range` (string): Time range
- `limit` (integer): Maximum results

### get_metrics

Retrieve time-series metrics.

**Parameters:**
- `metric_name` (string): Metric name
- `aggregation` (string): Aggregation type (avg, sum, min, max, p95, p99)
- `time_range` (string): Time range
- `labels` (object, optional): Label filters

### correlate_events

Find all related telemetry for a correlation ID.

**Parameters:**
- `correlation_id` (string): Correlation ID
- `include_types` (array): Types to include (traces, logs, metrics, events)

### analyze_incident

AI-powered root cause analysis for incidents.

**Parameters:**
- `time_range` (string): Time range to analyze
- `affected_services` (array): Services involved
- `symptoms` (array): Observed symptoms

## Architecture

```
AI Agent
    ↓
MCP Protocol
    ↓
MCP Server
    ↓
    ├─→ Elasticsearch (logs)
    ├─→ TimescaleDB (metrics)
    ├─→ ChromaDB (semantic search)
    └─→ Redis (caching)
```

## Performance

- Average query latency: <500ms
- Semantic search: <1s
- Cache hit rate: >70%

## License

MIT License
