# AI DevOps Best Practices

This document outlines best practices for implementing observability and DevOps practices for AI systems.

## Table of Contents

1. [Instrumentation](#instrumentation)
2. [Metrics Collection](#metrics-collection)
3. [Logging](#logging)
4. [Tracing](#tracing)
5. [Cost Management](#cost-management)
6. [Performance Optimization](#performance-optimization)
7. [Security](#security)
8. [Alerting](#alerting)

## Instrumentation

### Start Early
- Add observability instrumentation from the beginning of development
- Don't wait until production to add monitoring
- Include instrumentation in your definition of done

### Use Standard Frameworks
- Leverage OpenTelemetry for vendor-neutral instrumentation
- Use Prometheus for metrics when possible
- Follow semantic conventions for attributes

### Instrument at Multiple Levels
```python
# Application level
with tracer.start_as_current_span("ai_pipeline"):
    # Component level
    with tracer.start_as_current_span("preprocess"):
        data = preprocess(input)
    
    # Model level
    with tracer.start_as_current_span("inference"):
        result = model.predict(data)
```

## Metrics Collection

### Essential AI Metrics

#### Performance Metrics
- **Latency**: P50, P95, P99 response times
- **Throughput**: Requests per second
- **Token Generation Rate**: Tokens per second
- **Error Rate**: Percentage of failed requests

#### Cost Metrics
- **Token Usage**: Input and output tokens
- **Inference Cost**: Per-request cost
- **Total Spend**: Aggregate costs over time
- **Cost Per User**: Attribution of costs

#### Quality Metrics
- **Model Accuracy**: Prediction quality
- **Hallucination Rate**: Incorrect or fabricated responses
- **User Satisfaction**: Feedback scores
- **Model Drift**: Performance degradation over time

### Metric Naming Conventions

Follow Prometheus naming best practices:

```
<namespace>_<metric>_<unit>_<suffix>
```

Examples:
- `ai_inference_latency_seconds`
- `ai_tokens_used_total`
- `ai_inference_cost_dollars_total`

### Cardinality Management

Avoid high-cardinality labels:
```python
# ❌ Bad: User ID as label
metric.labels(user_id="user-12345")

# ✅ Good: User tier as label
metric.labels(user_tier="premium")
```

## Logging

### Structured Logging

Always use structured (JSON) logging:

```python
import json
import logging

logger.info(json.dumps({
    "timestamp": "2025-11-13T22:00:00Z",
    "level": "INFO",
    "message": "Inference completed",
    "model": "gpt-4",
    "latency_ms": 542,
    "tokens_used": 150,
    "trace_id": "abc123"
}))
```

### Log Levels

Use appropriate log levels:
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (degraded service)
- **ERROR**: Error messages (request failed)
- **CRITICAL**: Critical issues (service down)

### Trace Correlation

Always include trace IDs in logs:
```python
span = trace.get_current_span()
logger.info("Processing request", extra={
    "trace_id": span.get_span_context().trace_id,
    "span_id": span.get_span_context().span_id
})
```

## Tracing

### Span Naming

Use clear, consistent span names:
- Use verb-noun format: `process_request`, `generate_response`
- Include operation type: `http.request`, `db.query`
- Be consistent across services

### Span Attributes

Add relevant attributes:
```python
span.set_attribute("ai.model.name", "gpt-4")
span.set_attribute("ai.model.version", "1.0.0")
span.set_attribute("ai.tokens.input", 45)
span.set_attribute("ai.tokens.output", 150)
```

### Error Handling

Properly record exceptions:
```python
try:
    result = model.predict(data)
except Exception as e:
    span.record_exception(e)
    span.set_status(Status(StatusCode.ERROR, str(e)))
    raise
```

## Cost Management

### Track Token Usage

Monitor token consumption closely:
```python
total_tokens = input_tokens + output_tokens
cost = total_tokens * token_price
cost_metric.inc(cost)
```

### Set Budgets and Alerts

Configure alerts for cost thresholds:
- Daily spending limits
- Per-user limits
- Per-model limits

### Optimize Token Usage

- Use prompt compression
- Implement caching for common queries
- Choose appropriate models (don't use GPT-4 for simple tasks)
- Limit max_tokens parameter

## Performance Optimization

### Caching

Implement intelligent caching:
```python
@cache(ttl=3600)
def get_model_response(prompt_hash):
    return model.generate(prompt)
```

### Batching

Batch requests when possible:
```python
# Instead of multiple single requests
results = model.batch_predict(inputs)
```

### Model Selection

Choose the right model for the task:
- Simple tasks → Smaller, faster models
- Complex tasks → Larger, more capable models
- Balance cost, latency, and quality

### Connection Pooling

Reuse connections to AI services:
```python
client = OpenAIClient(
    pool_size=10,
    pool_timeout=30
)
```

## Security

### API Key Management

Never commit API keys:
```python
# ✅ Good: Use environment variables
api_key = os.getenv("OPENAI_API_KEY")

# ❌ Bad: Hardcoded keys
api_key = "sk-abc123..."
```

### Data Privacy

Protect sensitive data:
- Sanitize PII before logging
- Truncate user inputs in traces
- Use encryption for stored data

```python
# Truncate sensitive data
span.set_attribute("user.input", user_input[:50] + "...")
```

### Rate Limiting

Implement rate limits:
```python
@rate_limit(requests_per_minute=60)
def process_request(input):
    return model.predict(input)
```

## Alerting

### Alert on SLOs

Define Service Level Objectives (SLOs):
- Availability: 99.9% uptime
- Latency: P95 < 1s
- Error rate: < 0.1%

### Alert Thresholds

Set meaningful thresholds:
```promql
# High error rate
rate(ai_inference_errors_total[5m]) > 0.1

# High latency
histogram_quantile(0.95, rate(ai_inference_latency_seconds_bucket[5m])) > 1.0

# High cost
increase(ai_inference_cost_dollars_total[1h]) > 100
```

### Alert Fatigue Prevention

- Use multi-window alerting
- Implement alert grouping
- Set appropriate severity levels
- Include runbooks in alerts

### On-Call Runbooks

Create runbooks for common issues:
1. High error rate → Check service health, recent deployments
2. High latency → Check queue depth, resource utilization
3. High costs → Review token usage, check for abuse

## Continuous Improvement

### Review Metrics Regularly

- Weekly: Review dashboards and trends
- Monthly: Analyze cost and performance
- Quarterly: Reassess SLOs and alerts

### A/B Testing

Test model changes with A/B testing:
```python
if experiment_group == "A":
    model = "gpt-4"
else:
    model = "gpt-3.5-turbo"
```

### Feedback Loops

Collect and act on feedback:
- User satisfaction ratings
- Error reports
- Performance complaints

## References

- [OpenTelemetry Best Practices](https://opentelemetry.io/docs/concepts/best-practices/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Google SRE Book](https://sre.google/books/)
- [Observability Engineering](https://www.oreilly.com/library/view/observability-engineering/9781492076438/)
