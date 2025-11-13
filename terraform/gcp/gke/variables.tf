variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
}

variable "network_name" {
  description = "VPC network name"
  type        = string
}

variable "subnetwork_name" {
  description = "VPC subnetwork name"
  type        = string
}

variable "node_pools" {
  description = "Node pool configurations"
  type = map(object({
    machine_type      = string
    min_count         = number
    max_count         = number
    disk_size_gb      = number
    disk_type         = string
    preemptible       = bool
    spot              = bool
    accelerator_type  = string
    accelerator_count = number
  }))
}
