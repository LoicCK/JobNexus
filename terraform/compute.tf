# ------------------------------------------------------------------------------
# Cloud Run Backend Service
# ------------------------------------------------------------------------------

# Main application deployment on Cloud Run
resource "google_cloud_run_v2_service" "jobnexus_service" {
  provider = google
  project  = var.project_id
  location = var.region
  name     = "jobnexus-service"

  # Allow traffic from everywhere (public ingress)
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    timeout                          = "300s"
    service_account                  = google_service_account.run_sa.email
    max_instance_request_concurrency = 80

    # Autoscaling configuration
    scaling {
      max_instance_count = 20
      min_instance_count = 0
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/jobnexus-repo/jobnexus-app"

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
        startup_cpu_boost = true
      }

      ports {
        container_port = 8080
      }

      # Environment variables
      env {
        name  = "FORCE_UPDATE"
        value = "1"
      }

      # Secrets injection as environment variables
      env {
        name = "FT_CLIENT_ID"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.ft_client_id.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "FT_CLIENT_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.ft_client_secret.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "LBA_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.lba_api_key.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "WTTJ_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.wttj_api_key.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "WTTJ_APP_ID"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.wttj_app_id.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "BIGQUERY_TABLE_ID"
        value = "${var.project_id}.${google_bigquery_dataset.job_data.dataset_id}.${google_bigquery_table.job_table.table_id}"
      }

      # Startup probe to check if the app is ready
      startup_probe {
        initial_delay_seconds = 0
        timeout_seconds       = 240
        period_seconds        = 240
        failure_threshold     = 1
        tcp_socket {
          port = 8080
        }
      }
    }
  }

  # Ignore changes to specific fields to prevent accidental overwrites during updates
  lifecycle {
    ignore_changes = [
      client,
      client_version,
      template[0].containers[0].image
    ]
  }

  depends_on = [
    google_secret_manager_secret_iam_member.run_sa_access
  ]
}

# ------------------------------------------------------------------------------
# Cloud Run Frontend Service
# ------------------------------------------------------------------------------

resource "google_cloud_run_v2_service" "jobnexus_frontend" {
  provider = google
  project  = var.project_id
  location = var.region
  name     = "jobnexus-frontend"

  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    timeout = "300s"
    service_account = google_service_account.run_sa.email

    scaling {
      max_instance_count = 10
      min_instance_count = 0
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/jobnexus-repo/jobnexus-frontend"

      resources {
        limits = {
          cpu    = "1000m"
          memory = "1Gi"
        }
        startup_cpu_boost = true
      }

      ports {
        container_port = 8080
      }

      env {
        name = "BACKEND_URL"
        value = google_cloud_run_v2_service.jobnexus_service.uri
      }

      env {
        name  = "BIGQUERY_PROJECT"
        value = var.project_id
      }
    }
  }

  lifecycle {
    ignore_changes = [
      client,
      client_version,
      template[0].containers[0].image
    ]
  }
}
