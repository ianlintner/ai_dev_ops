# Datadog Integration for AI Monitoring

This directory contains configurations and examples for monitoring AI workloads with Datadog.

## Setup

### Installation

```bash
pip install ddtrace datadog-api-client
```

### Configuration

Set environment variables:

```bash
export DD_API_KEY="your-datadog-api-key"
export DD_SITE="datadoghq.com"  # or datadoghq.eu, etc.
export DD_SERVICE="ai-inference-service"
export DD_ENV="production"
export DD_VERSION="1.0.0"
```

## Instrumentation

### Automatic Instrumentation

Use `ddtrace-run` for automatic instrumentation:

```bash
ddtrace-run python your_ai_app.py
```

### Manual Instrumentation

```python
from ddtrace import tracer, patch_all
from datadog import initialize, statsd

# Enable automatic instrumentation for common libraries
patch_all()

# Initialize Datadog
initialize(statsd_host='localhost', statsd_port=8125)

# Create custom spans
@tracer.wrap(service="ai-inference", resource="model.predict")
def ai_inference(prompt):
    span = tracer.current_span()
    span.set_tag("model.name", "gpt-4")
    span.set_tag("prompt.length", len(prompt))
    
    result = model.predict(prompt)
    
    span.set_tag("tokens.used", result.tokens)
    span.set_metric("inference.latency", result.latency)
    
    return result

# Send custom metrics
def track_metrics(model, tokens, cost):
    statsd.increment('ai.inference.requests', tags=[f"model:{model}"])
    statsd.histogram('ai.tokens.used', tokens, tags=[f"model:{model}"])
    statsd.gauge('ai.inference.cost', cost, tags=[f"model:{model}"])
```

## Metrics

### Custom Metrics Example

```python
from datadog import statsd

# Counter
statsd.increment('ai.inference.count', tags=['model:gpt-4', 'status:success'])

# Histogram
statsd.histogram('ai.inference.latency', 0.542, tags=['model:gpt-4'])

# Gauge
statsd.gauge('ai.active_requests', 12, tags=['model:gpt-4'])

# Distribution
statsd.distribution('ai.token.generation.rate', 67.8, tags=['model:gpt-4'])

# Set
statsd.set('ai.unique_users', 'user-123', tags=['model:gpt-4'])
```

## Dashboard Configuration

### Datadog Dashboard JSON

```json
{
  "title": "AI Model Performance",
  "description": "Monitor AI inference metrics",
  "widgets": [
    {
      "definition": {
        "title": "Inference Requests per Second",
        "type": "timeseries",
        "requests": [
          {
            "q": "sum:ai.inference.requests{*}.as_rate()",
            "display_type": "line"
          }
        ]
      }
    },
    {
      "definition": {
        "title": "Average Latency by Model",
        "type": "timeseries",
        "requests": [
          {
            "q": "avg:ai.inference.latency{*} by {model}",
            "display_type": "line"
          }
        ]
      }
    },
    {
      "definition": {
        "title": "Token Usage",
        "type": "query_value",
        "requests": [
          {
            "q": "sum:ai.tokens.used{*}",
            "aggregator": "sum"
          }
        ]
      }
    },
    {
      "definition": {
        "title": "Error Rate",
        "type": "timeseries",
        "requests": [
          {
            "q": "sum:ai.inference.requests{status:error}.as_rate() / sum:ai.inference.requests{*}.as_rate()",
            "display_type": "line"
          }
        ]
      }
    }
  ],
  "template_variables": [
    {
      "name": "model",
      "prefix": "model",
      "default": "*"
    },
    {
      "name": "environment",
      "prefix": "env",
      "default": "production"
    }
  ],
  "layout_type": "ordered"
}
```

## Monitors (Alerts)

### High Latency Monitor

```json
{
  "name": "AI Inference High Latency",
  "type": "metric alert",
  "query": "avg(last_5m):avg:ai.inference.latency{env:production} by {model} > 1",
  "message": "AI inference latency is high for {{model.name}}. Current: {{value}}s @slack-ai-alerts",
  "tags": ["service:ai-inference", "alert:latency"],
  "options": {
    "thresholds": {
      "critical": 1.0,
      "warning": 0.8
    },
    "notify_no_data": true,
    "no_data_timeframe": 10
  }
}
```

### High Error Rate Monitor

```json
{
  "name": "AI Inference High Error Rate",
  "type": "metric alert",
  "query": "sum(last_10m):sum:ai.inference.requests{status:error}.as_count() / sum:ai.inference.requests{*}.as_count() > 0.05",
  "message": "AI inference error rate is above 5% @pagerduty-ai",
  "tags": ["service:ai-inference", "alert:errors"],
  "options": {
    "thresholds": {
      "critical": 0.05,
      "warning": 0.02
    }
  }
}
```

### Cost Alert Monitor

```json
{
  "name": "AI Inference Cost Alert",
  "type": "metric alert",
  "query": "sum(last_1h):sum:ai.inference.cost{*} > 100",
  "message": "AI inference cost exceeded $100/hour @slack-finance",
  "tags": ["service:ai-inference", "alert:cost"]
}
```

## APM Configuration

### Service Configuration

```python
from ddtrace import config

# Configure service
config.service = "ai-inference-service"
config.env = "production"
config.version = "1.0.0"

# Configure trace sampling
config.analytics_enabled = True
config.analytics_sample_rate = 1.0

# Configure trace filters
config.http.trace_query_string = True
```

## Log Integration

### Structured Logging with Datadog

```python
import logging
import json
from ddtrace import tracer

def setup_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    
    class DatadogFormatter(logging.Formatter):
        def format(self, record):
            # Get current trace context
            span = tracer.current_span()
            
            log_record = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
            }
            
            # Add trace correlation
            if span:
                log_record["dd.trace_id"] = span.trace_id
                log_record["dd.span_id"] = span.span_id
            
            # Add custom fields
            if hasattr(record, "model"):
                log_record["model"] = record.model
            
            return json.dumps(log_record)
    
    handler.setFormatter(DatadogFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Use the logger
logger = logging.getLogger(__name__)
logger.info("Inference completed", extra={"model": "gpt-4", "tokens": 150})
```

## Synthetic Monitoring

Create synthetic tests for AI endpoints:

```json
{
  "name": "AI Inference API Test",
  "type": "api",
  "config": {
    "request": {
      "method": "POST",
      "url": "https://api.example.com/inference",
      "body": "{\"prompt\": \"test\"}",
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer {{API_KEY}}"
      }
    },
    "assertions": [
      {
        "type": "statusCode",
        "operator": "is",
        "target": 200
      },
      {
        "type": "responseTime",
        "operator": "lessThan",
        "target": 1000
      }
    ]
  },
  "locations": ["aws:us-east-1", "aws:eu-west-1"],
  "options": {
    "tick_every": 300,
    "min_failure_duration": 0,
    "min_location_failed": 1
  }
}
```

## Best Practices

1. **Use tags consistently** for filtering and grouping
2. **Enable APM** for distributed tracing
3. **Configure log correlation** with trace IDs
4. **Set up monitors** before going to production
5. **Use service level objectives (SLOs)** for availability targets
6. **Monitor costs** with custom metrics

## Common Tags

Standardize tags across services:

```python
common_tags = [
    f"env:{os.getenv('DD_ENV')}",
    f"service:{os.getenv('DD_SERVICE')}",
    f"version:{os.getenv('DD_VERSION')}",
    "team:ai-platform",
    "cost_center:engineering"
]
```

## Profiling

Enable continuous profiler:

```python
from ddtrace.profiling import Profiler

profiler = Profiler()
profiler.start()
```

## Troubleshooting

### Traces not appearing?
1. Verify DD_API_KEY is set
2. Check Datadog Agent is running
3. Verify network connectivity to Datadog

### High costs?
1. Adjust sampling rate
2. Review indexed spans
3. Optimize log volume
4. Use metric-based monitors instead of log-based

## Resources

- [Datadog APM Documentation](https://docs.datadoghq.com/tracing/)
- [Datadog Python Tracer](https://ddtrace.readthedocs.io/)
- [DogStatsD](https://docs.datadoghq.com/developers/dogstatsd/)
