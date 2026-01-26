resource "google_service_account" "run_sa" {
  account_id = "jobnexus-run-sa"
  display_name = "Cloud Run identity"
}

data "google_project" "project" {
}

resource "google_project_iam_member" "run_secret_access" {
  member  = "serviceAccount:${google_service_account.run_sa.email}"
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
}

resource "google_cloud_run_v2_service_iam_member" "gateway_invoker" {
  project = var.project_id
  location = var.region
  member   = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  name   = google_cloud_run_v2_service.jobnexus_service.name
  role   = "roles/run.invoker"
}

resource "google_artifact_registry_repository" "jobnexus_repo" {
  provider      = google
  project       = var.project_id
  location      = var.region
  repository_id = "jobnexus-repo"
  format        = "DOCKER"
  description   = "Repository Docker for JobNexus"

  cleanup_policies {
    action = "KEEP"
    id     = "Archives of previous builds"
    most_recent_versions {
      keep_count = 2
    }
  }
}

resource "google_cloud_run_v2_service" "jobnexus_service" {
  provider = google
  project  = var.project_id
  location = var.region
  name     = "jobnexus-service"
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    timeout                          = "300s"
    service_account                  = google_service_account.run_sa.email
    max_instance_request_concurrency = 80
    
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

      env {
        name  = "FORCE_UPDATE"
        value = "1"
      }

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

resource "google_secret_manager_secret" "lba_api_key" {
  project   = var.project_id
  secret_id = "la-bonne-alternance-api-key"
  replication {
    auto {}
  }
}

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

resource "google_api_gateway_api" "jobnexus_api" {
  provider     = google-beta
  project      = var.project_id
  api_id       = "jobnexus-api"
  display_name = "jobnexus-api"
}

resource "google_api_gateway_api_config" "jobnexus_config" {
  provider      = google-beta
  project       = var.project_id
  api           = google_api_gateway_api.jobnexus_api.api_id
  api_config_id = "jobnexus-conf-v3" 
  display_name  = "jobnexus-conf-v3"

  openapi_documents {
    document {
      path     = "openapi-jobnexus.json"
      contents = filebase64("openapi-jobnexus.json")
    }
  }
}

resource "google_api_gateway_gateway" "jobnexus_gateway" {
  provider     = google-beta
  project      = var.project_id
  api_config   = google_api_gateway_api_config.jobnexus_config.id
  gateway_id   = "jobnexus-gateway"
  region       = "europe-west1"
  display_name = "jobnexus-gateway"
}