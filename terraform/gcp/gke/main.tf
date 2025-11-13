# GKE Cluster Module

resource "google_container_cluster" "primary" {
  name     = "${var.environment}-${var.cluster_name}"
  location = var.region
  project  = var.project_id

  # Use regional cluster for high availability
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = var.network_name
  subnetwork = var.subnetwork_name

  # IP allocation policy for VPC-native cluster
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Enable Autopilot features
  release_channel {
    channel = "REGULAR"
  }

  # Monitoring and logging
  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
    managed_prometheus {
      enabled = true
    }
  }

  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  # Network policy
  network_policy {
    enabled = true
  }

  # Binary authorization
  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    gcp_filestore_csi_driver_config {
      enabled = true
    }
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }
  }

  # Master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All"
    }
  }

  # Private cluster config
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  lifecycle {
    ignore_changes = [node_pool, initial_node_count]
  }
}

# Node Pools
resource "google_container_node_pool" "pools" {
  for_each = var.node_pools

  name       = each.key
  location   = var.region
  cluster    = google_container_cluster.primary.name
  project    = var.project_id
  node_count = each.value.min_count

  autoscaling {
    min_node_count = each.value.min_count
    max_node_count = each.value.max_count
  }

  node_config {
    preemptible  = each.value.preemptible
    spot         = each.value.spot
    machine_type = each.value.machine_type
    disk_size_gb = each.value.disk_size_gb
    disk_type    = each.value.disk_type

    # GPU configuration
    dynamic "guest_accelerator" {
      for_each = each.value.accelerator_type != "" ? [1] : []
      content {
        type  = each.value.accelerator_type
        count = each.value.accelerator_count
      }
    }

    # Service account with minimal permissions
    service_account = google_service_account.node_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      environment = var.environment
      node_pool   = each.key
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Shielded instance config
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# Service account for node pools
resource "google_service_account" "node_sa" {
  account_id   = "${var.environment}-${var.cluster_name}-node-sa"
  display_name = "GKE Node Service Account"
  project      = var.project_id
}

# IAM bindings for node service account
resource "google_project_iam_member" "node_sa_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.node_sa.email}"
}

resource "google_project_iam_member" "node_sa_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.node_sa.email}"
}

resource "google_project_iam_member" "node_sa_monitoring_viewer" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.node_sa.email}"
}

resource "google_project_iam_member" "node_sa_artifact_registry" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.node_sa.email}"
}
