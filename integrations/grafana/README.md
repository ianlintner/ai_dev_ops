# Grafana Integration for AI Monitoring

This directory contains pre-built Grafana dashboards and alert configurations for monitoring AI workloads.

## Dashboards

### AI Model Performance Dashboard (`ai-metrics-dashboard.json`)

A comprehensive dashboard for monitoring AI inference performance including:

- **Inference Requests per Second**: Track request throughput by model and status
- **Average Inference Latency**: Monitor response times across models
- **Token Usage**: Track token consumption by model and type
- **Error Rate**: Monitor failures with built-in alerting
- **Active Inferences**: Real-time view of concurrent requests
- **Cost Tracking**: Monitor inference costs
- **P95 Latency**: Track tail latencies
- **Token Generation Rate**: Monitor generation performance

## Installation

### Import Dashboard

1. Open Grafana UI
2. Navigate to Dashboards → Import
3. Upload `ai-metrics-dashboard.json`
4. Select your Prometheus data source
5. Click Import

### Configure Data Source

Ensure your Prometheus data source is scraping metrics from your AI services:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'ai-inference'
    static_configs:
      - targets: ['ai-service:8000']
    scrape_interval: 15s
```

## Variables

The dashboard includes template variables:

- **model**: Filter by AI model (multi-select)
- **environment**: Filter by environment (single-select)

## Alerts

### High Error Rate Alert

- **Condition**: Error rate > 0.1 errors/sec
- **Frequency**: Evaluated every 1 minute
- **Message**: "AI inference error rate is high"

### Configure Alert Notifications

1. Navigate to Alerting → Notification channels
2. Add your preferred channel (Slack, PagerDuty, email, etc.)
3. Link to the "High Error Rate" alert

## Custom Queries

### Total Requests (24h)
```promql
increase(ai_inference_requests_total[24h])
```

### Success Rate
```promql
sum(rate(ai_inference_requests_total{status="success"}[5m])) / sum(rate(ai_inference_requests_total[5m])) * 100
```

### Cost per 1000 Requests
```promql
increase(ai_inference_cost_dollars_total[1h]) / (increase(ai_inference_requests_total[1h]) / 1000)
```

### Model Comparison
```promql
avg by (model) (rate(ai_inference_latency_seconds_sum[5m]) / rate(ai_inference_latency_seconds_count[5m]))
```

## Annotations

The dashboard supports annotations for:
- Deployments
- Configuration changes
- Incidents

Add annotations via Grafana API or UI to track events alongside metrics.

## Troubleshooting

### No Data Displayed

1. Verify Prometheus is scraping your AI service
2. Check that metrics endpoint is accessible
3. Ensure metric names match the dashboard queries
4. Verify data source configuration in Grafana

### Missing Metrics

If certain panels show no data:
1. Ensure the corresponding metrics are being exported
2. Check Prometheus targets page for scrape errors
3. Verify metric labels match dashboard queries

## Customization

To customize the dashboard:
1. Edit in Grafana UI
2. Save changes
3. Export JSON for version control
4. Share with team

## Best Practices

1. Set appropriate refresh intervals (30s recommended)
2. Configure alert thresholds based on your SLOs
3. Use dashboard variables for flexibility
4. Add annotations for deployments and incidents
5. Create dashboard links for related views
6. Set up notification channels before enabling alerts
