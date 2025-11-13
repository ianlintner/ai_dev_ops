# OpenTelemetry Examples

This directory contains examples demonstrating OpenTelemetry instrumentation for AI workloads.

## Files

### `basic_instrumentation.py`
Basic OpenTelemetry tracing for AI inference pipeline:
- Demonstrates span creation
- Shows how to add attributes
- Includes events and annotations
- Exports traces to console

**Run:**
```bash
python basic_instrumentation.py
```

### `advanced_agent_tracing.py`
Advanced tracing with custom metrics for AI agents:
- Multi-step workflows
- Custom metrics (counters, histograms)
- Tool call tracking
- Error handling and exception tracking
- Context propagation

**Run:**
```bash
python advanced_agent_tracing.py
```

## Key Concepts

### Spans
Spans represent operations in your application:
```python
with tracer.start_as_current_span("operation_name") as span:
    # Your code here
    span.set_attribute("key", "value")
```

### Attributes
Add context to spans:
```python
span.set_attribute("ai.model.name", "gpt-4")
span.set_attribute("ai.tokens.used", 150)
```

### Events
Mark significant points in time:
```python
span.add_event("inference_started", {
    "model": "gpt-4",
    "timestamp": time.time()
})
```

### Status
Indicate success or failure:
```python
from opentelemetry.trace import Status, StatusCode

# Success
span.set_status(Status(StatusCode.OK))

# Error
span.set_status(Status(StatusCode.ERROR, "error message"))
```

## Exporting Traces

### Console Exporter (Development)
```python
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
exporter = ConsoleSpanExporter()
```

### OTLP Exporter (Production)
```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
exporter = OTLPSpanExporter(endpoint="http://collector:4317")
```

### Jaeger Exporter
```python
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
```

## Best Practices

1. **Meaningful Span Names**: Use descriptive names like `preprocess_input`, not `process_1`
2. **Add Context**: Include relevant attributes (model name, token count, etc.)
3. **Handle Errors**: Always record exceptions with `span.record_exception(e)`
4. **Batch Processing**: Use `BatchSpanProcessor` for better performance
5. **Sampling**: Configure sampling for high-volume applications

## Semantic Conventions

Follow OpenTelemetry semantic conventions for AI:
- `ai.model.name`: Model name (e.g., "gpt-4")
- `ai.model.version`: Model version
- `ai.tokens.input`: Input tokens
- `ai.tokens.output`: Output tokens
- `ai.inference.latency_ms`: Inference latency

## Integration

### With Azure Monitor
See [examples/azure/azure_monitor_example.py](../azure/azure_monitor_example.py)

### With Prometheus
Combine with Prometheus metrics:
```python
from opentelemetry.instrumentation.prometheus import PrometheusMetricsExporter
```

## Troubleshooting

### Spans not appearing?
1. Check exporter configuration
2. Verify trace provider is set
3. Allow time for batch processing

### High overhead?
1. Adjust sampling rate
2. Use async exporters
3. Increase batch size

## Further Reading

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [Semantic Conventions](https://opentelemetry.io/docs/reference/specification/trace/semantic_conventions/)
- [Best Practices](../../docs/best-practices.md)
