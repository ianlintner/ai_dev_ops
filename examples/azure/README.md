# Azure AI Monitoring Examples

This directory contains examples for monitoring AI workloads using Azure Monitor and Application Insights.

## Prerequisites

- Azure subscription
- Application Insights resource
- Azure Monitor OpenTelemetry Python package

## Setup

1. Install dependencies:
```bash
pip install azure-monitor-opentelemetry azure-identity
```

2. Set environment variable with your Application Insights connection string:
```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/"
```

## Running Examples

```bash
python azure_monitor_example.py
```

## What Gets Monitored

### Traces
- Request processing spans
- AI inference operations
- Batch processing operations
- Custom events and attributes

### Metrics
- Inference request counts
- Inference duration histograms
- Custom business metrics

### Properties
- Agent ID
- Model name
- User ID
- Cloud provider and region
- Token usage
- Input/output lengths

## Viewing Data in Azure

1. **Application Insights → Transaction Search**: View individual traces
2. **Application Insights → Performance**: Analyze operation durations
3. **Application Insights → Failures**: Monitor errors and exceptions
4. **Application Insights → Metrics**: View custom metrics
5. **Application Insights → Live Metrics**: Real-time monitoring

## Example Queries (Kusto/KQL)

### Average inference duration
```kusto
traces
| where name == "ai_inference"
| extend duration = todouble(customDimensions.duration_ms)
| summarize avg(duration) by bin(timestamp, 5m)
```

### Token usage over time
```kusto
traces
| where name == "ai_inference"
| extend tokens = toint(customDimensions["tokens.used"])
| summarize total_tokens = sum(tokens) by bin(timestamp, 1h)
```

### Error rate
```kusto
traces
| where name == "process_request"
| summarize 
    total = count(),
    errors = countif(customDimensions.status == "error")
| extend error_rate = todouble(errors) / total * 100
```

## Alerts Configuration

Configure alerts in Azure Monitor for:
- High error rates
- Elevated latency
- Token usage thresholds
- Cost limits

## Best Practices

1. Use consistent span naming conventions
2. Add custom dimensions for business context
3. Set up alerts for critical metrics
4. Use sampling for high-volume workloads
5. Monitor costs and token usage
6. Track model performance metrics
