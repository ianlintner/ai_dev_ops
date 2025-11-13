# Cloud Monitoring Configuration

# Notification Channel (Email)
resource "google_monitoring_notification_channel" "email" {
  display_name = "${var.environment} AI DevOps Alerts"
  type         = "email"
  project      = var.project_id

  labels = {
    email_address = "alerts@example.com"
  }
}

# Alert Policy: High Inference Latency
resource "google_monitoring_alert_policy" "high_latency" {
  display_name = "${var.environment} High AI Inference Latency"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "High Latency Threshold"

    condition_threshold {
      filter          = "metric.type=\"custom.googleapis.com/ai/inference_latency\" AND resource.type=\"k8s_container\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 1000  # milliseconds

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert Policy: High Error Rate
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "${var.environment} High AI Error Rate"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "Error Rate Threshold"

    condition_threshold {
      filter          = "metric.type=\"custom.googleapis.com/ai/error_rate\" AND resource.type=\"k8s_container\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05  # 5%

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }
}

# Alert Policy: High Token Usage
resource "google_monitoring_alert_policy" "high_token_usage" {
  display_name = "${var.environment} High Token Usage"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "Token Usage Threshold"

    condition_threshold {
      filter          = "metric.type=\"custom.googleapis.com/ai/tokens_used\" AND resource.type=\"k8s_container\""
      duration        = "3600s"
      comparison      = "COMPARISON_GT"
      threshold_value = 1000000

      aggregations {
        alignment_period   = "3600s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }
}

# Log-based Metric for Error Count
resource "google_logging_metric" "error_count" {
  name    = "${var.environment}_ai_error_count"
  project = var.project_id
  filter  = "resource.type=\"k8s_container\" AND severity>=ERROR AND labels.app=\"ai-inference\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"

    labels {
      key         = "error_type"
      value_type  = "STRING"
      description = "Type of error"
    }
  }

  label_extractors = {
    "error_type" = "EXTRACT(jsonPayload.error_type)"
  }
}

# Dashboard
resource "google_monitoring_dashboard" "ai_services" {
  dashboard_json = jsonencode({
    displayName = "${var.environment} AI Services Dashboard"
    mosaicLayout = {
      columns = 12
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Inference Latency"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"custom.googleapis.com/ai/inference_latency\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_MEAN"
                      crossSeriesReducer = "REDUCE_MEAN"
                    }
                  }
                }
                plotType = "LINE"
              }]
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          widget = {
            title = "Inference Count"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"custom.googleapis.com/ai/inference_count\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                    }
                  }
                }
                plotType = "LINE"
              }]
            }
          }
        },
        {
          width  = 6
          height = 4
          yPos   = 4
          widget = {
            title = "Error Rate"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"custom.googleapis.com/ai/error_rate\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_MEAN"
                      crossSeriesReducer = "REDUCE_MEAN"
                    }
                  }
                }
                plotType = "LINE"
              }]
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          yPos   = 4
          widget = {
            title = "Token Usage"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"custom.googleapis.com/ai/tokens_used\" resource.type=\"k8s_container\""
                    aggregation = {
                      alignmentPeriod    = "3600s"
                      perSeriesAligner   = "ALIGN_SUM"
                      crossSeriesReducer = "REDUCE_SUM"
                    }
                  }
                }
                plotType = "LINE"
              }]
            }
          }
        }
      ]
    }
  })
  project = var.project_id
}
