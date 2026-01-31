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
