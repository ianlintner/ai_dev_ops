# Azure Monitor Configuration

This directory contains configurations and examples for Azure Monitor integration.

## Files

- `azure_monitor_example.py`: Example implementation with Azure Monitor
- `README.md`: This file

## Setup

### Prerequisites

1. Azure subscription
2. Application Insights resource
3. Connection string from Application Insights

### Installation

```bash
pip install azure-monitor-opentelemetry azure-identity
```

### Configuration

Set environment variable with your connection string:

```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/"
```

## Terraform Configuration

```hcl
# Create Application Insights resource
resource "azurerm_application_insights" "ai_monitoring" {
  name                = "ai-monitoring"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  
  tags = {
    environment = "production"
    service     = "ai-inference"
  }
}

output "instrumentation_key" {
  value     = azurerm_application_insights.ai_monitoring.instrumentation_key
  sensitive = true
}

output "connection_string" {
  value     = azurerm_application_insights.ai_monitoring.connection_string
  sensitive = true
}
```

## Alert Rules

### Terraform Alert Configuration

```hcl
resource "azurerm_monitor_metric_alert" "high_latency" {
  name                = "ai-high-latency-alert"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_application_insights.ai_monitoring.id]
  description         = "Alert when AI inference latency is high"

  criteria {
    metric_namespace = "Microsoft.Insights/components"
    metric_name      = "requests/duration"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 1000  # 1 second
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

resource "azurerm_monitor_metric_alert" "high_error_rate" {
  name                = "ai-high-error-rate-alert"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_application_insights.ai_monitoring.id]

  criteria {
    metric_namespace = "Microsoft.Insights/components"
    metric_name      = "requests/failed"
    aggregation      = "Count"
    operator         = "GreaterThan"
    threshold        = 10
  }
}
```

## Kusto Queries

### Top 10 Slowest Requests
```kusto
requests
| where timestamp > ago(1h)
| where name contains "ai_inference"
| top 10 by duration desc
| project timestamp, name, duration, resultCode, customDimensions
```

### Error Analysis
```kusto
exceptions
| where timestamp > ago(24h)
| summarize count() by type, outerMessage
| order by count_ desc
```

### Token Usage by User
```kusto
traces
| where timestamp > ago(24h)
| extend tokens = toint(customDimensions["tokens.used"])
| extend user_id = tostring(customDimensions["user.id"])
| summarize total_tokens = sum(tokens) by user_id
| order by total_tokens desc
```

### Cost Tracking
```kusto
traces
| where timestamp > ago(7d)
| extend cost = todouble(customDimensions["ai.cost"])
| summarize total_cost = sum(cost) by bin(timestamp, 1d)
| render timechart
```

## Dashboard Configuration

Create a custom Azure Dashboard:

```json
{
  "properties": {
    "lenses": {
      "0": {
        "order": 0,
        "parts": {
          "0": {
            "position": {
              "x": 0,
              "y": 0,
              "colSpan": 6,
              "rowSpan": 4
            },
            "metadata": {
              "type": "Extension/AppInsights/PartType/MetricsChartPart",
              "settings": {
                "title": "AI Inference Latency",
                "metrics": [
                  {
                    "resourceId": "/subscriptions/.../Microsoft.Insights/components/ai-monitoring",
                    "name": "requests/duration",
                    "aggregationType": 4
                  }
                ]
              }
            }
          }
        }
      }
    }
  }
}
```

## Best Practices

1. **Use connection strings instead of instrumentation keys** (newer approach)
2. **Enable sampling for high-volume applications**
3. **Configure appropriate retention policies**
4. **Set up alerts before going to production**
5. **Use custom dimensions for business context**
6. **Implement log correlation with trace IDs**

## Sampling Configuration

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

configure_azure_monitor(
    connection_string=connection_string,
    sampler=TraceIdRatioBased(0.1)  # Sample 10% of traces
)
```

## Cost Optimization

1. **Use sampling** to reduce data ingestion costs
2. **Set data retention** based on compliance needs
3. **Archive old data** to cheaper storage
4. **Use daily cap** to prevent unexpected costs

## Troubleshooting

### Data not appearing?
1. Verify connection string is correct
2. Check firewall rules allow outbound to *.in.applicationinsights.azure.com
3. Wait 2-5 minutes for data to appear
4. Check Application Insights → Live Metrics

### High costs?
1. Review sampling configuration
2. Check data volume in Usage and estimated costs
3. Reduce custom dimension cardinality
4. Consider using cheaper data retention tiers

## Resources

- [Azure Monitor Documentation](https://learn.microsoft.com/azure/azure-monitor/)
- [Application Insights for Python](https://learn.microsoft.com/azure/azure-monitor/app/opencensus-python)
- [Kusto Query Language](https://learn.microsoft.com/azure/data-explorer/kusto/query/)
