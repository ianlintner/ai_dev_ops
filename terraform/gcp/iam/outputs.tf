output "ai_inference_service_account_email" {
  description = "AI Inference Service Account email"
  value       = google_service_account.ai_inference.email
}

output "ai_inference_service_account_name" {
  description = "AI Inference Service Account name"
  value       = google_service_account.ai_inference.name
}
