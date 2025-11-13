# Datadog Agent Configuration for AI Services

This directory contains configuration and examples for integrating AI services with Datadog.

## Features

- **APM (Application Performance Monitoring)**: Distributed tracing for AI pipelines
- **Custom Metrics**: AI-specific metrics (latency, tokens, cost)
- **Log Management**: Structured logs with trace correlation
- **Dashboards**: Pre-built dashboards for AI monitoring
- **Monitors**: Alerts for anomalies and SLO violations

## Prerequisites

- Datadog account and API key
- Datadog Agent installed (version 7.x or higher)
- Python packages: `ddtrace`, `datadog`

```bash
pip install ddtrace datadog
```

## Quick Start

### 1. Install Datadog Agent

**Kubernetes (Helm):**
```bash
helm repo add datadog https://helm.datadoghq.com
helm repo update

helm install datadog datadog/datadog \
  --set datadog.apiKey=<YOUR_API_KEY> \
  --set datadog.appKey=<YOUR_APP_KEY> \
  --set datadog.site='datadoghq.com' \
  --set datadog.apm.enabled=true \
  --set datadog.logs.enabled=true \
  --set datadog.logs.containerCollectAll=true
```

**Docker:**
```bash
docker run -d --name datadog-agent \
  -e DD_API_KEY=<YOUR_API_KEY> \
  -e DD_SITE="datadoghq.com" \
  -e DD_APM_ENABLED=true \
  -e DD_LOGS_ENABLED=true \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /proc/:/host/proc/:ro \
  -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
  datadog/agent:latest
```

### 2. Configure Environment Variables

```bash
export DD_AGENT_HOST=localhost
export DD_TRACE_AGENT_PORT=8126
export DD_STATSD_PORT=8125
export DD_ENV=production
export DD_SERVICE=ai-inference-service
export DD_VERSION=1.0.0
```

### 3. Run the Example

```bash
python datadog_apm_example.py
```

### 4. Automatic Instrumentation

For automatic instrumentation, use `ddtrace-run`:

```bash
ddtrace-run python your_ai_service.py
```

## Custom Metrics

### Inference Metrics

```python
from datadog import statsd

# Increment counter
statsd.increment('ai.inference.count', tags=['model:gpt-4'])

# Record latency
statsd.histogram('ai.inference.latency', 542, tags=['model:gpt-4'])

# Track tokens
statsd.gauge('ai.tokens.used', 150, tags=['model:gpt-4', 'type:output'])

# Cost tracking
statsd.increment('ai.cost.total', 0.003, tags=['model:gpt-4'])
```

### Service Health

```python
statsd.service_check(
    'ai.inference.health',
    statsd.OK,
    tags=['service:ai-inference']
)
```

## Distributed Tracing

### Manual Instrumentation

```python
from ddtrace import tracer

@tracer.wrap(name='ai.inference', service='ai-inference')
def model_inference(input_data):
    span = tracer.current_span()
    span.set_tag('model.name', 'gpt-4')
    span.set_tag('tokens.used', 150)
    # Your code here
```

### Trace Context Propagation

```python
import requests
from ddtrace.propagation.http import HTTPPropagator

# Inject trace context into HTTP headers
headers = {}
HTTPPropagator.inject(tracer.current_span().context, headers)
response = requests.get('http://api.example.com', headers=headers)
```

## Log Management

### Structured Logging with Trace Correlation

```python
import logging
import json
from ddtrace import tracer

# Configure JSON logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

span = tracer.current_span()
logger.info(json.dumps({
    'message': 'Inference completed',
    'model': 'gpt-4',
    'latency_ms': 542,
    'dd.trace_id': span.trace_id,
    'dd.span_id': span.span_id,
}))
```

## Dashboards

### Import Pre-built Dashboard

1. Log in to Datadog
2. Navigate to Dashboards → New Dashboard
3. Import the JSON from `integrations/datadog/ai-metrics-dashboard.json`

### Key Metrics Visualized

- Inference requests per second
- P50, P95, P99 latency
- Error rate
- Token usage and cost
- Model performance comparison

## Monitors and Alerts

### High Latency Alert

```yaml
name: "High AI Inference Latency"
type: metric alert
query: "avg(last_5m):avg:ai.inference.latency{*} > 1000"
message: |
  AI inference latency is above 1000ms
  Current: {{value}}ms
  Notify: @slack-alerts
```

### High Error Rate

```yaml
name: "High AI Error Rate"
type: metric alert
query: "sum(last_5m):sum:ai.pipeline.error{*}.as_count() > 10"
message: |
  AI inference error rate is elevated
  Errors: {{value}}
  Notify: @pagerduty
```

### Cost Threshold

```yaml
name: "High AI Cost"
type: metric alert
query: "sum(last_1h):sum:ai.cost.total{*} > 100"
message: |
  AI costs exceeded $100 in the last hour
  Total: ${{value}}
  Notify: @finance-team
```

## APM Service Map

View the service map to see:
- Service dependencies
- Request flow
- Latency by service
- Error rates

Access: https://app.datadoghq.com/apm/map

## Best Practices

### 1. Tagging Strategy

Use consistent tags:
```python
tags = [
    f'model:{model_name}',
    f'env:{environment}',
    f'version:{version}',
    f'user.tier:{user_tier}'
]
```

### 2. Sampling

For high-traffic services, configure sampling:
```python
tracer.configure(
    priority_sampling=True,
    analytics_enabled=True,
)
```

### 3. Resource Naming

Use meaningful resource names:
```python
@tracer.wrap(resource='model_inference_gpt4')
def inference():
    pass
```

### 4. Error Tracking

Always track errors:
```python
try:
    result = model.predict(data)
except Exception as e:
    span.set_tag('error', True)
    span.set_tag('error.msg', str(e))
    span.set_tag('error.type', type(e).__name__)
    raise
```

## Troubleshooting

### Agent Not Receiving Traces

1. Check agent status:
```bash
datadog-agent status
```

2. Verify connectivity:
```bash
curl http://localhost:8126/info
```

3. Check environment variables:
```bash
echo $DD_AGENT_HOST
echo $DD_TRACE_AGENT_PORT
```

### Metrics Not Appearing

1. Verify StatsD configuration
2. Check metric names for typos
3. Ensure tags are properly formatted
4. Check agent logs: `/var/log/datadog/agent.log`

## References

- [Datadog APM Documentation](https://docs.datadoghq.com/tracing/)
- [Datadog Python Library](https://docs.datadoghq.com/tracing/setup_overview/setup/python/)
- [Custom Metrics Guide](https://docs.datadoghq.com/metrics/custom_metrics/)
- [Log Management](https://docs.datadoghq.com/logs/)
