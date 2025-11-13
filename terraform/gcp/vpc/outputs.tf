output "network_name" {
  description = "VPC network name"
  value       = google_compute_network.vpc.name
}

output "network_id" {
  description = "VPC network ID"
  value       = google_compute_network.vpc.id
}

output "subnetwork_name" {
  description = "Subnetwork name"
  value       = google_compute_subnetwork.subnet.name
}

output "subnetwork_id" {
  description = "Subnetwork ID"
  value       = google_compute_subnetwork.subnet.id
}
