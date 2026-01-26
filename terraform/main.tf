# ------------------------------------------------------------------------------
# Service Accounts & IAM Permissions
# ------------------------------------------------------------------------------

# Service Account for the Cloud Run application
resource "google_service_account" "run_sa" {
  account_id   = "jobnexus-run-sa"
  display_name = "Cloud Run identity"
}

# Service Account for the API Gateway
resource "google_service_account" "gateway_sa" {
  account_id   = "jobnexus-gateway-sa"
  display_name = "API Gateway Service Account"
}

# Data source to access project details
data "google_project" "project" {
}

# Grant the Cloud Run Service Account access to Secret Manager
resource "google_project_iam_member" "run_secret_access" {
  member  = "serviceAccount:${google_service_account.run_sa.email}"
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
}

# Allow the API Gateway Service Account to invoke the Cloud Run service
resource "google_cloud_run_v2_service_iam_member" "gateway_invoker" {
  project  = var.project_id
  location = var.region
  member   = "serviceAccount:${google_service_account.gateway_sa.email}"
  role     = "roles/run.invoker"
  name     = google_cloud_run_v2_service.jobnexus_service.name
}

# ------------------------------------------------------------------------------
# Artifact Registry
# ------------------------------------------------------------------------------

# Docker repository to store application images
resource "google_artifact_registry_repository" "jobnexus_repo" {
  provider      = google
  project       = var.project_id
  location      = var.region
  repository_id = "jobnexus-repo"
  format        = "DOCKER"
  description   = "Repository Docker for JobNexus"

  # Keep only the 2 most recent versions to save storage
  cleanup_policies {
    action = "KEEP"
    id     = "Archives of previous builds"
    most_recent_versions {
      keep_count = 2
    }
  }
}

# ------------------------------------------------------------------------------
# Cloud Run Service
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
    google_project_iam_member.run_secret_access
  ]
}

# ------------------------------------------------------------------------------
# Secret Manager Secrets
# ------------------------------------------------------------------------------

# Secrets for France Travail API
resource "google_secret_manager_secret" "ft_client_id" {
  project   = var.project_id
  secret_id = "france-travail-id"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "ft_client_secret" {
  project   = var.project_id
  secret_id = "france-travail-secret"
  replication {
    auto {}
  }
}

# Secret for La Bonne Alternance API
resource "google_secret_manager_secret" "lba_api_key" {
  project   = var.project_id
  secret_id = "la-bonne-alternance-api-key"
  replication {
    auto {}
  }
}

# Secrets for Welcome To The Jungle API
resource "google_secret_manager_secret" "wttj_api_key" {
  project   = var.project_id
  secret_id = "wttj-api-key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "wttj_app_id" {
  project   = var.project_id
  secret_id = "wttj-app-id"
  replication {
    auto {}
  }
}

# ------------------------------------------------------------------------------
# API Gateway
# ------------------------------------------------------------------------------

# Define the API Gateway API resource
resource "google_api_gateway_api" "jobnexus_api" {
  provider     = google-beta
  project      = var.project_id
  api_id       = "jobnexus-api"
  display_name = "jobnexus-api"
}

# Configure the API Gateway with the OpenAPI spec
resource "google_api_gateway_api_config" "jobnexus_config" {
  provider      = google-beta
  project       = var.project_id
  api           = google_api_gateway_api.jobnexus_api.api_id
  api_config_id_prefix = "jobnexus-conf-"
  display_name  = "jobnexus-conf-v3"

  gateway_config {
    backend_config {
      google_service_account = google_service_account.gateway_sa.email
    }
  }

  # Load OpenAPI spec and inject Cloud Run URL
  openapi_documents {
    document {
      path     = "openapi-jobnexus.json"
      contents = base64encode(templatefile("openapi-jobnexus.json", {
        cloud_run_url = google_cloud_run_v2_service.jobnexus_service.uri
      }))
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Deploy the API Gateway
resource "google_api_gateway_gateway" "jobnexus_gateway" {
  provider     = google-beta
  project      = var.project_id
  api_config   = google_api_gateway_api_config.jobnexus_config.id
  gateway_id   = "jobnexus-gateway"
  region       = var.region
  display_name = "jobnexus-gateway"
}