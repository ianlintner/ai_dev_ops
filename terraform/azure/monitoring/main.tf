# Monitoring Module - Application Insights and Log Analytics

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.cluster_name}-logs"
  location            = var.azure_region
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_analytics_retention_days

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "${var.cluster_name}-insights"
  location            = var.azure_region
  resource_group_name = var.resource_group_name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.main.id
  retention_in_days   = var.application_insights_retention_days

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

# Metric Alerts

# High Latency Alert
resource "azurerm_monitor_metric_alert" "high_latency" {
  name                = "${var.cluster_name}-high-latency"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_application_insights.main.id]
  description         = "Alert when AI inference latency exceeds threshold"
  severity            = 2
  frequency           = "PT5M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "microsoft.insights/components"
    metric_name      = "requests/duration"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 1000 # 1 second in milliseconds
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }

  tags = merge(
    var.tags,
    {
      Environment = var.environment
      AlertType   = "Performance"
    }
  )
}

# High Error Rate Alert
resource "azurerm_monitor_metric_alert" "high_error_rate" {
  name                = "${var.cluster_name}-high-error-rate"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_application_insights.main.id]
  description         = "Alert when error rate is high"
  severity            = 1
  frequency           = "PT5M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "microsoft.insights/components"
    metric_name      = "requests/failed"
    aggregation      = "Count"
    operator         = "GreaterThan"
    threshold        = 10
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }

  tags = merge(
    var.tags,
    {
      Environment = var.environment
      AlertType   = "Reliability"
    }
  )
}

# Action Group for Notifications
resource "azurerm_monitor_action_group" "main" {
  name                = "${var.cluster_name}-action-group"
  resource_group_name = var.resource_group_name
  short_name          = "aidevops"

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}
