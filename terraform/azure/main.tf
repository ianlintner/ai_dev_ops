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
      # WARNING: Setting prevent_deletion_if_contains_resources = false allows Terraform to delete resource groups
      # even if they contain resources. This is potentially dangerous and should NOT be used in production environments.
      # This setting is intended for development/testing environments only.
      prevent_deletion_if_contains_resources = false
    }
    key_vault {
      # Setting purge_soft_delete_on_destroy = false maintains Azure Key Vault's soft delete protection,
      # which prevents accidental permanent deletion. Set to true only in development/testing environments.
      purge_soft_delete_on_destroy = false
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

  resource_group_name   = module.resource_group.name
  azure_region          = var.azure_region
  environment           = var.environment
  vnet_address_space    = var.vnet_address_space
  subnet_address_prefix = var.subnet_address_prefix
  tags                  = var.tags
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
}

# AKS Cluster Module
module "aks" {
  source = "./aks"

  resource_group_name            = module.resource_group.name
  azure_region                   = var.azure_region
  cluster_name                   = var.cluster_name
  kubernetes_version             = var.kubernetes_version
  subnet_id                      = module.vnet.subnet_id
  node_pools                     = var.node_pools
  environment                    = var.environment
  log_analytics_workspace_id     = module.monitoring.log_analytics_workspace_id
  tags                           = var.tags
}
