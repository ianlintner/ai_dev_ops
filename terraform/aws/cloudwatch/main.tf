# CloudWatch Monitoring for AI Services

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ai_services" {
  name              = "/aws/ai-devops/${var.cluster_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.environment}-ai-services-logs"
    Environment = var.environment
  }
}

# CloudWatch Log Group for Application Logs
resource "aws_cloudwatch_log_group" "application" {
  name              = "/aws/ai-devops/${var.cluster_name}/application"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.environment}-application-logs"
  }
}

# Container Insights
resource "aws_cloudwatch_log_group" "container_insights_performance" {
  count             = var.enable_container_insights ? 1 : 0
  name              = "/aws/containerinsights/${var.cluster_name}/performance"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.environment}-container-insights"
  }
}

# CloudWatch Metric Alarms

# High Inference Latency Alarm
resource "aws_cloudwatch_metric_alarm" "high_latency" {
  alarm_name          = "${var.environment}-ai-high-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "InferenceLatency"
  namespace           = "AIDevOps"
  period              = 300
  statistic           = "Average"
  threshold           = 1000  # milliseconds
  alarm_description   = "This metric monitors AI inference latency"
  treat_missing_data  = "notBreaching"

  dimensions = {
    Environment = var.environment
    ClusterName = var.cluster_name
  }

  tags = {
    Name = "${var.environment}-high-latency-alarm"
  }
}

# High Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.environment}-ai-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ErrorRate"
  namespace           = "AIDevOps"
  period              = 300
  statistic           = "Average"
  threshold           = 5  # percent
  alarm_description   = "This metric monitors AI inference error rate"
  treat_missing_data  = "notBreaching"

  dimensions = {
    Environment = var.environment
    ClusterName = var.cluster_name
  }

  tags = {
    Name = "${var.environment}-high-error-rate-alarm"
  }
}

# High Token Usage Alarm
resource "aws_cloudwatch_metric_alarm" "high_token_usage" {
  alarm_name          = "${var.environment}-ai-high-token-usage"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TokensUsed"
  namespace           = "AIDevOps"
  period              = 3600  # 1 hour
  statistic           = "Sum"
  threshold           = 1000000  # tokens per hour
  alarm_description   = "This metric monitors token usage"
  treat_missing_data  = "notBreaching"

  dimensions = {
    Environment = var.environment
    ClusterName = var.cluster_name
  }

  tags = {
    Name = "${var.environment}-high-token-usage-alarm"
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "ai_services" {
  dashboard_name = "${var.environment}-ai-services-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AIDevOps", "InferenceLatency", { stat = "Average" }],
            ["...", { stat = "p95" }],
            ["...", { stat = "p99" }]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "Inference Latency"
          yAxis = {
            left = {
              label = "Milliseconds"
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AIDevOps", "InferenceCount", { stat = "Sum" }]
          ]
          period = 300
          stat   = "Sum"
          region = data.aws_region.current.name
          title  = "Inference Count"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AIDevOps", "ErrorRate", { stat = "Average" }]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "Error Rate (%)"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AIDevOps", "TokensUsed", { stat = "Sum" }]
          ]
          period = 3600
          stat   = "Sum"
          region = data.aws_region.current.name
          title  = "Token Usage"
        }
      },
      {
        type = "log"
        properties = {
          query   = "SOURCE '/aws/ai-devops/${var.cluster_name}/application' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20"
          region  = data.aws_region.current.name
          title   = "Recent Errors"
        }
      }
    ]
  })
}

data "aws_region" "current" {}
