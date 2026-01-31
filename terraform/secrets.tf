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
