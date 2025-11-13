# Variables for GCP Infrastructure

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
  default     = "ai-devops-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version for GKE"
  type        = string
  default     = "1.28"
}

variable "network_name" {
  description = "Name of the VPC network"
  type        = string
  default     = "ai-devops-network"
}

variable "node_pools" {
  description = "GKE node pool configurations"
  type = map(object({
    machine_type   = string
    min_count      = number
    max_count      = number
    disk_size_gb   = number
    disk_type      = string
    preemptible    = bool
    spot           = bool
    accelerator_type = string
    accelerator_count = number
  }))
  default = {
    default = {
      machine_type      = "n2-standard-4"
      min_count         = 2
      max_count         = 10
      disk_size_gb      = 100
      disk_type         = "pd-standard"
      preemptible       = false
      spot              = false
      accelerator_type  = ""
      accelerator_count = 0
    }
    gpu = {
      machine_type      = "n1-standard-4"
      min_count         = 0
      max_count         = 5
      disk_size_gb      = 200
      disk_type         = "pd-standard"
      preemptible       = false
      spot              = true
      accelerator_type  = "nvidia-tesla-t4"
      accelerator_count = 1
    }
  }
}
