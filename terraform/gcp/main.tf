# GCP Infrastructure for AI DevOps
# This module provisions a GKE cluster with monitoring for AI workloads

terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# VPC Module
module "vpc" {
  source = "./vpc"

  project_id  = var.project_id
  environment = var.environment
  region      = var.region
  network_name = var.network_name
}

# GKE Module
module "gke" {
  source = "./gke"

  project_id         = var.project_id
  environment        = var.environment
  region             = var.region
  cluster_name       = var.cluster_name
  kubernetes_version = var.kubernetes_version
  network_name       = module.vpc.network_name
  subnetwork_name    = module.vpc.subnetwork_name
  node_pools         = var.node_pools
}

# IAM Module
module "iam" {
  source = "./iam"

  project_id   = var.project_id
  environment  = var.environment
  cluster_name = var.cluster_name
}

# Cloud Monitoring Module
module "monitoring" {
  source = "./monitoring"

  project_id   = var.project_id
  environment  = var.environment
  cluster_name = var.cluster_name
}
