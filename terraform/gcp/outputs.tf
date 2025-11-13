# Outputs for GCP Infrastructure

output "network_name" {
  description = "VPC network name"
  value       = module.vpc.network_name
}

output "subnetwork_name" {
  description = "VPC subnetwork name"
  value       = module.vpc.subnetwork_name
}

output "cluster_name" {
  description = "GKE cluster name"
  value       = module.gke.cluster_name
}

output "cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = module.gke.cluster_endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "GKE cluster CA certificate"
  value       = module.gke.cluster_ca_certificate
  sensitive   = true
}

output "service_account_email" {
  description = "Service account email for AI workloads"
  value       = module.iam.ai_inference_service_account_email
}

output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${var.cluster_name} --region ${var.region} --project ${var.project_id}"
}
