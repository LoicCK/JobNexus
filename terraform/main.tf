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

# Service Account for the Cloud Scheduler
resource "google_service_account" "scheduler_sa" {
  account_id = "jobnexus-scheduler-sa"
  display_name = "Cloud Scheduler Service Account"
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

resource "google_cloud_run_v2_service_iam_member" "job_invoker" {
  project  = var.project_id
  location = var.region
  member = "serviceAccount:${google_service_account.scheduler_sa.email}"
  name   = google_cloud_run_v2_service.jobnexus_service.name
  role   = "roles/run.invoker"
}

resource "google_project_iam_member" "run_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_project_iam_member" "run_bq_read_session_user" {
  project = var.project_id
  role    = "roles/bigquery.readSessionUser"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_service_account" "build_sa" {
  account_id   = "jobnexus-build-sa"
  display_name = "Cloud Build Service Account"
}

resource "google_project_iam_member" "build_logs" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.build_sa.email}"
}

resource "google_artifact_registry_repository_iam_member" "build_push" {
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.jobnexus_repo.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.build_sa.email}"
}

resource "google_project_iam_member" "build_run_admin" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.build_sa.email}"
}

resource "google_service_account_iam_member" "build_act_as_run_sa" {
  service_account_id = google_service_account.run_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.build_sa.email}"
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


locals {
  openapi_content = templatefile("openapi-jobnexus.json", {
    cloud_run_url = google_cloud_run_v2_service.jobnexus_service.uri
  })
}

# Configure the API Gateway with the OpenAPI spec
resource "google_api_gateway_api_config" "jobnexus_config" {
  provider      = google-beta
  project       = var.project_id
  api           = google_api_gateway_api.jobnexus_api.api_id
  api_config_id_prefix = "jobnexus-conf-"
  display_name  = "jobnexus-conf-${substr(md5(local.openapi_content), 0, 7)}"

  gateway_config {
    backend_config {
      google_service_account = google_service_account.gateway_sa.email
    }
  }

  # Load OpenAPI spec and inject Cloud Run URL
  openapi_documents {
    document {
      path     = "openapi-jobnexus.json"
      contents = base64encode(local.openapi_content)
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

# ------------------------------------------------------------------------------
# Firestore Cache
# ------------------------------------------------------------------------------

resource "google_project_service" "firestore" {
  project            = var.project_id
  service            = "firestore.googleapis.com"
  disable_on_destroy = false
}

resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.firestore]
}

resource "google_firestore_field" "job_searches_ttl" {
  project    = var.project_id
  database   = google_firestore_database.database.name
  collection = "job_searches"
  field      = "expire_at"

  ttl_config {}

  depends_on = [google_firestore_database.database]
}

# ------------------------------------------------------------------------------
# BigQuery Database
# ------------------------------------------------------------------------------

resource "google_bigquery_dataset" "job_data" {
  dataset_id                  = "jobnexus_job_data"
  friendly_name               = "JobNexus Data"
  description                 = "Jobs history for market analysis"
  location                    = var.region
  delete_contents_on_destroy = true

  labels = {
    env     = "production"
    project = "jobnexus"
  }
}
resource "google_bigquery_dataset_iam_member" "cloud_run_bq_access" {
  dataset_id = google_bigquery_dataset.job_data.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_bigquery_table" "job_table" {
  dataset_id = google_bigquery_dataset.job_data.dataset_id
  table_id   = "jobnexus_job_table"

  time_partitioning {
    type = "DAY"
  }

    schema = <<EOF
[
  {
    "name": "search_query",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Search query"
  },
  {
    "name": "job_hash",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Unique hash of the job offer for deduplication"
  },
  {
    "name": "title",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Title of the job offer"
  },
  {
    "name": "company",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Name of the company"
  },
  {
    "name": "city",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "City in which the job offer is located"
  },
  {
    "name": "url",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "URL to access the job offer"
  },
  {
    "name": "contract_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Type of the contract"
  },
  {
    "name": "target_diploma_level",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The target diploma level of the job offer"
  },
  {
    "name": "source",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Job offer source"
  },
  {
    "name": "scraped_at",
    "type": "TIMESTAMP",
    "mode": "NULLABLE",
    "description": "Timestamp at which the job offer was scraped"
  }
]
EOF
}

# ------------------------------------------------------------------------------
# Cloud Scheduler
# ------------------------------------------------------------------------------

resource "google_cloud_scheduler_job" "data_job" {
  for_each = var.jobs
  name = "jobnexus-search-${lower(each.value)}"
  description = "A job to gather new offers every day"
  schedule = "0 6 * * *"
  time_zone = "Europe/Paris"
  attempt_deadline = "320s"

  retry_config {
    retry_count = 2
  }

  http_target {
    http_method = "GET"
    uri = "${google_cloud_run_v2_service.jobnexus_service.uri}/search?q=${each.value}&latitude=${var.default_latitude}&longitude=${var.default_longitude}&radius=${var.default_radius}&insee=${var.default_insee}"
    oidc_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }
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
          memory = "512Mi"
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

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.jobnexus_frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ------------------------------------------------------------------------------
# Cloud Build Triggers
# ------------------------------------------------------------------------------

resource "google_cloudbuildv2_connection" "github_connection" {
  project  = var.project_id
  location = var.region
  name     = "LoicCK-Github"

  github_config {
  }

  lifecycle {
    ignore_changes = [
      github_config
    ]
  }
}

resource "google_cloudbuildv2_repository" "jobnexus_repo_link" {
  project           = var.project_id
  location          = var.region
  name              = "jobnexus-repo"
  parent_connection = google_cloudbuildv2_connection.github_connection.name
  remote_uri        = "https://github.com/LoicCK/JobNexus.git"
}

resource "google_cloudbuild_trigger" "backend_trigger" {
  project  = var.project_id
  location = var.region
  name     = "jobnexus-backend-trigger"

  description = "Backend trigger"

  service_account = google_service_account.build_sa.id

  repository_event_config {
    repository = google_cloudbuildv2_repository.jobnexus_repo_link.id
    push {
      branch = "^main$"
    }
  }

  included_files = ["backend/**"]
  filename       = "backend/cloudbuild.yaml"
}

resource "google_cloudbuild_trigger" "frontend_trigger" {
  project  = var.project_id
  location = var.region
  name     = "jobnexus-frontend-trigger"

  description = "Frontend trigger"

  service_account = google_service_account.build_sa.id

  repository_event_config {
    repository = google_cloudbuildv2_repository.jobnexus_repo_link.id
    push {
      branch = "^main$"
    }
  }

  included_files = ["frontend/**"]
  filename       = "frontend/cloudbuild.yaml"
}
