# Getting Started with AI DevOps

This guide will help you get started with implementing observability for your AI systems.

## Quick Start

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/ianlintner/ai_dev_ops.git
cd ai_dev_ops

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Run Your First Example

```bash
# Run OpenTelemetry example
cd examples/opentelemetry
python basic_instrumentation.py
```

You should see traces output to the console showing the AI inference pipeline execution.

### 3. Start Prometheus Metrics

```bash
# Run Prometheus metrics example
cd examples/prometheus
python ai_metrics.py
```

Open http://localhost:8000 to view raw metrics. The metrics will update as the simulation runs.

### 4. Set Up Grafana (Optional)

If you have Grafana installed:

```bash
# Import the dashboard
# 1. Open Grafana UI
# 2. Go to Dashboards → Import
# 3. Upload integrations/grafana/ai-metrics-dashboard.json
```

## Adding Observability to Your AI Application

### Step 1: Add OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

# Configure tracing
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)
trace.set_tracer_provider(tracer_provider)

# Get a tracer
tracer = trace.get_tracer(__name__)
```

### Step 2: Instrument Your Code

```python
def ai_inference(prompt):
    with tracer.start_as_current_span("ai_inference") as span:
        # Add attributes
        span.set_attribute("model", "gpt-4")
        span.set_attribute("prompt_length", len(prompt))
        
        # Your AI code here
        result = model.generate(prompt)
        
        # Add more attributes
        span.set_attribute("tokens_used", result.tokens)
        
        return result
```

### Step 3: Add Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
inference_counter = Counter(
    'ai_inference_requests_total',
    'Total inference requests',
    ['model', 'status']
)

inference_latency = Histogram(
    'ai_inference_latency_seconds',
    'Inference latency',
    ['model']
)

# Use metrics
def ai_inference(prompt):
    with inference_latency.labels(model="gpt-4").time():
        result = model.generate(prompt)
        inference_counter.labels(model="gpt-4", status="success").inc()
        return result

# Start metrics server
start_http_server(8000)
```

### Step 4: Add Structured Logging

```python
import logging
import json
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Use structured logging
logger.info("Inference completed", extra={
    "model": "gpt-4",
    "latency_ms": 542,
    "tokens_used": 150
})
```

## Architecture Patterns

### Pattern 1: Centralized Monitoring

```
┌─────────────┐     ┌──────────────┐
│ AI Service  │────▶│ Prometheus   │
│             │     └──────────────┘
│ (metrics)   │            │
└─────────────┘            │
                           ▼
┌─────────────┐     ┌──────────────┐
│ AI Service  │────▶│ Grafana      │
│             │     │ (dashboards) │
│ (traces)    │────▶└──────────────┘
└─────────────┘
```

### Pattern 2: Cloud-Native with Azure

```
┌─────────────┐
│ AI Service  │
│             │
│ OpenTelemetry│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Azure       │
│ Monitor     │
│             │
│ - Traces    │
│ - Metrics   │
│ - Logs      │
└─────────────┘
```

### Pattern 3: Multi-Service Tracing

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ API     │────▶│ AI      │────▶│ Model   │
│ Gateway │     │ Service │     │ Service │
└─────────┘     └─────────┘     └─────────┘
     │               │               │
     └───────────────┴───────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ Trace        │
              │ Collector    │
              └──────────────┘
```

## Common Use Cases

### Use Case 1: Monitor Model Performance

```python
# Track model accuracy over time
accuracy_gauge = Gauge('ai_model_accuracy', 'Model accuracy', ['model'])

def evaluate_model(predictions, labels):
    accuracy = calculate_accuracy(predictions, labels)
    accuracy_gauge.labels(model="gpt-4").set(accuracy)
```

### Use Case 2: Track Token Costs

```python
# Monitor token usage and costs
def track_costs(model, input_tokens, output_tokens):
    total_tokens = input_tokens + output_tokens
    cost = calculate_cost(model, input_tokens, output_tokens)
    
    token_counter.labels(model=model).inc(total_tokens)
    cost_counter.labels(model=model).inc(cost)
```

### Use Case 3: Debug Slow Requests

```python
# Add detailed spans for debugging
with tracer.start_as_current_span("request") as request_span:
    with tracer.start_as_current_span("preprocess") as pre_span:
        data = preprocess(input)
        pre_span.set_attribute("duration_ms", get_duration())
    
    with tracer.start_as_current_span("inference") as inf_span:
        result = model.predict(data)
        inf_span.set_attribute("duration_ms", get_duration())
```

## Next Steps

1. **Review Examples**: Explore the examples directory for complete implementations
2. **Read Best Practices**: Check out [best-practices.md](./best-practices.md)
3. **Configure Integrations**: Set up Grafana, Azure Monitor, or Datadog
4. **Implement Alerts**: Configure alerting for critical metrics
5. **Iterate**: Continuously improve based on observability data

## Troubleshooting

### No metrics showing up?

1. Check that the metrics endpoint is accessible: `curl http://localhost:8000`
2. Verify Prometheus is scraping your service
3. Check for errors in application logs

### Traces not appearing?

1. Verify OpenTelemetry is configured correctly
2. Check exporter configuration
3. Ensure spans are being created with `start_as_current_span`

### High costs?

1. Review token usage metrics
2. Implement caching for common queries
3. Use smaller models for simple tasks
4. Set rate limits per user

## Resources

- [Examples Directory](../examples/): Complete code examples
- [Data Formats](../data-formats/): Schema definitions
- [Integrations](../integrations/): Platform configurations
- [Best Practices](./best-practices.md): Detailed guidelines

## Getting Help

- Open an issue in this repository
- Check existing issues for solutions
- Review the examples for reference implementations
