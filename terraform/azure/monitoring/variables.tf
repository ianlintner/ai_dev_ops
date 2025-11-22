variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "azure_region" {
  description = "Azure region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "application_insights_retention_days" {
  description = "Retention period for Application Insights data"
  type        = number
  default     = 90
}

variable "log_analytics_retention_days" {
  description = "Retention period for Log Analytics data"
  type        = number
  default     = 90
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
