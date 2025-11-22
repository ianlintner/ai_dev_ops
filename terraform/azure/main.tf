# Azure Infrastructure for AI DevOps
# This module provisions an AKS cluster with monitoring for AI workloads

terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }

  skip_provider_registration = false
}

# Resource Group Module
module "resource_group" {
  source = "./resource-group"

  resource_group_name = var.resource_group_name
  azure_region        = var.azure_region
  environment         = var.environment
  tags                = var.tags
}

# Virtual Network Module
module "vnet" {
  source = "./vnet"

  resource_group_name = module.resource_group.name
  azure_region        = var.azure_region
  environment         = var.environment
  vnet_address_space  = var.vnet_address_space
  subnet_address_prefix = var.subnet_address_prefix
  tags                = var.tags

  depends_on = [module.resource_group]
}

# Monitoring Module (Application Insights + Log Analytics) - Created before AKS
module "monitoring" {
  source = "./monitoring"

  resource_group_name                 = module.resource_group.name
  azure_region                        = var.azure_region
  environment                         = var.environment
  cluster_name                        = var.cluster_name
  application_insights_retention_days = var.application_insights_retention_days
  log_analytics_retention_days        = var.log_analytics_retention_days
  tags                                = var.tags

  depends_on = [module.resource_group]
}

# AKS Cluster Module
module "aks" {
  source = "./aks"

  resource_group_name = module.resource_group.name
  azure_region        = var.azure_region
  cluster_name        = var.cluster_name
  kubernetes_version  = var.kubernetes_version
  subnet_id           = module.vnet.subnet_id
  node_pools          = var.node_pools
  environment         = var.environment
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  tags                = var.tags

  depends_on = [module.vnet, module.monitoring]
}
