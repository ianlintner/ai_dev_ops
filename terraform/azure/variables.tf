# Variables for Azure Infrastructure

variable "azure_region" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "ai-devops-rg"
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
  default     = "ai-devops-aks"
}

variable "kubernetes_version" {
  description = "Kubernetes version for AKS"
  type        = string
  default     = "1.28"
}

variable "vnet_address_space" {
  description = "Address space for VNet"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_address_prefix" {
  description = "Address prefix for AKS subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "node_pools" {
  description = "AKS node pool configurations"
  type = map(object({
    vm_size             = string
    node_count          = number
    min_count           = number
    max_count           = number
    enable_auto_scaling = bool
    max_pods            = number
  }))
  default = {
    system = {
      vm_size             = "Standard_D4s_v3"
      node_count          = 3
      min_count           = 2
      max_count           = 10
      enable_auto_scaling = true
      max_pods            = 110
    }
    ai_workload = {
      vm_size             = "Standard_D8s_v3"
      node_count          = 3
      min_count           = 2
      max_count           = 20
      enable_auto_scaling = true
      max_pods            = 110
    }
  }
}

variable "application_insights_retention_days" {
  description = "Application Insights data retention in days"
  type        = number
  default     = 90
}

variable "log_analytics_retention_days" {
  description = "Log Analytics workspace retention in days"
  type        = number
  default     = 90
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project   = "ai-devops"
    ManagedBy = "terraform"
  }
}
