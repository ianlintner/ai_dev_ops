# IAM Configuration for AI Services on GKE

# Service Account for AI Inference
resource "google_service_account" "ai_inference" {
  account_id   = "${var.environment}-ai-inference"
  display_name = "AI Inference Service Account"
  project      = var.project_id
}

# Workload Identity binding
resource "google_service_account_iam_member" "ai_inference_workload_identity" {
  service_account_id = google_service_account.ai_inference.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[ai-services/ai-inference]"
}

# Cloud Logging permissions
resource "google_project_iam_member" "ai_inference_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.ai_inference.email}"
}

# Cloud Monitoring permissions
resource "google_project_iam_member" "ai_inference_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.ai_inference.email}"
}

# Cloud Trace permissions
resource "google_project_iam_member" "ai_inference_trace" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.ai_inference.email}"
}

# Secret Manager permissions
resource "google_project_iam_member" "ai_inference_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.ai_inference.email}"
}

# Vertex AI permissions (for AI workloads)
resource "google_project_iam_member" "ai_inference_vertex" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.ai_inference.email}"
}
