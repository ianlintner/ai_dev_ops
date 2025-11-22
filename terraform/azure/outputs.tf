# Outputs for Azure Infrastructure

output "resource_group_name" {
  description = "Name of the resource group"
  value       = module.resource_group.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = module.resource_group.location
}

output "vnet_id" {
  description = "ID of the virtual network"
  value       = module.vnet.vnet_id
}

output "subnet_id" {
  description = "ID of the AKS subnet"
  value       = module.vnet.subnet_id
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = module.aks.cluster_name
}

output "aks_cluster_id" {
  description = "ID of the AKS cluster"
  value       = module.aks.cluster_id
}

output "aks_cluster_endpoint" {
  description = "Endpoint for the AKS cluster"
  value       = module.aks.cluster_endpoint
}

output "aks_cluster_fqdn" {
  description = "FQDN of the AKS cluster"
  value       = module.aks.cluster_fqdn
}

output "application_insights_id" {
  description = "ID of Application Insights resource"
  value       = module.monitoring.application_insights_id
}

output "application_insights_key" {
  description = "Instrumentation key for Application Insights"
  value       = module.monitoring.application_insights_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Connection string for Application Insights"
  value       = module.monitoring.application_insights_connection_string
  sensitive   = true
}

output "log_analytics_workspace_id" {
  description = "ID of the Log Analytics workspace"
  value       = module.monitoring.log_analytics_workspace_id
}

output "log_analytics_workspace_name" {
  description = "Name of the Log Analytics workspace"
  value       = module.monitoring.log_analytics_workspace_name
}

output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "az aks get-credentials --resource-group ${module.resource_group.name} --name ${module.aks.cluster_name}"
}
