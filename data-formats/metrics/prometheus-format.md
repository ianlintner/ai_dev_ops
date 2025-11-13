# Prometheus Metrics Format Examples

## Standard Prometheus Format

### Counter Metric
```prometheus
# HELP ai_inference_requests_total Total number of AI inference requests
# TYPE ai_inference_requests_total counter
ai_inference_requests_total{model="gpt-4",environment="production",status="success"} 15423
ai_inference_requests_total{model="gpt-4",environment="production",status="error"} 87
ai_inference_requests_total{model="claude-2",environment="production",status="success"} 9876
```

### Histogram Metric
```prometheus
# HELP ai_inference_latency_seconds Time taken for AI inference
# TYPE ai_inference_latency_seconds histogram
ai_inference_latency_seconds_bucket{model="gpt-4",le="0.1"} 234
ai_inference_latency_seconds_bucket{model="gpt-4",le="0.25"} 1245
ai_inference_latency_seconds_bucket{model="gpt-4",le="0.5"} 8976
ai_inference_latency_seconds_bucket{model="gpt-4",le="1.0"} 14532
ai_inference_latency_seconds_bucket{model="gpt-4",le="2.5"} 15234
ai_inference_latency_seconds_bucket{model="gpt-4",le="+Inf"} 15423
ai_inference_latency_seconds_sum{model="gpt-4"} 7854.32
ai_inference_latency_seconds_count{model="gpt-4"} 15423
```

### Gauge Metric
```prometheus
# HELP ai_active_inferences Number of currently active inference requests
# TYPE ai_active_inferences gauge
ai_active_inferences{model="gpt-4"} 12
ai_active_inferences{model="claude-2"} 8
```

### Summary Metric
```prometheus
# HELP ai_token_generation_rate Token generation rate quantiles
# TYPE ai_token_generation_rate summary
ai_token_generation_rate{model="gpt-4",quantile="0.5"} 45.2
ai_token_generation_rate{model="gpt-4",quantile="0.9"} 78.9
ai_token_generation_rate{model="gpt-4",quantile="0.99"} 125.6
ai_token_generation_rate_sum{model="gpt-4"} 945632.8
ai_token_generation_rate_count{model="gpt-4"} 15423
```

## Best Practices

1. **Naming Convention**: Use `<namespace>_<metric>_<unit>` format
2. **Labels**: Use consistent label names across metrics
3. **Cardinality**: Limit label value combinations to avoid high cardinality
4. **Units**: Include unit in metric name (e.g., `_seconds`, `_bytes`)
5. **Type**: Always include TYPE and HELP comments
