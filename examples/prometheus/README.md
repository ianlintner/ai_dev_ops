"""
README for Prometheus Examples

This directory contains examples for monitoring AI models using Prometheus.
"""

# Prometheus Metrics Examples

## Overview

These examples demonstrate how to instrument AI inference workloads with Prometheus metrics.

## Files

- `ai_metrics.py`: Basic Prometheus metrics for AI model monitoring

## Metrics Collected

### Counters
- `ai_inference_requests_total`: Total inference requests by model and status
- `ai_tokens_used_total`: Total tokens consumed by model and type
- `ai_inference_cost_dollars_total`: Total inference cost in dollars
- `ai_inference_errors_total`: Total errors by model and error type

### Histograms
- `ai_inference_latency_seconds`: Inference latency distribution
- `ai_token_generation_rate_tokens_per_second`: Token generation rate distribution

### Gauges
- `ai_active_inferences`: Currently active inference requests

### Info
- `ai_model`: Model metadata and configuration

## Running the Examples

### Install dependencies
```bash
pip install prometheus-client
```

### Run the metrics server
```bash
python ai_metrics.py
```

### View metrics
Open your browser to http://localhost:8000 to see the raw Prometheus metrics.

### Example Prometheus configuration
```yaml
scrape_configs:
  - job_name: 'ai-inference'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
```

## Visualizing Metrics

### Example Prometheus queries

**Average inference latency:**
```promql
rate(ai_inference_latency_seconds_sum[5m]) / rate(ai_inference_latency_seconds_count[5m])
```

**Requests per second:**
```promql
rate(ai_inference_requests_total[1m])
```

**Error rate:**
```promql
rate(ai_inference_errors_total[5m])
```

**Token usage by model:**
```promql
sum by (model) (rate(ai_tokens_used_total[5m]))
```

**Total cost per hour:**
```promql
rate(ai_inference_cost_dollars_total[1h]) * 3600
```

## Integration with Grafana

Import the dashboard from `/integrations/grafana/ai-metrics-dashboard.json` to visualize these metrics.
