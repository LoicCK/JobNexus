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
