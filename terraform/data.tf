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

  schema = file("${path.module}/schemas/job_table.json")
}
