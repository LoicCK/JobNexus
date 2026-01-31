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

resource "google_secret_manager_secret_iam_member" "run_sa_access" {
  for_each  = toset(var.run_sa_secrets)
  project   = var.project_id
  secret_id = each.key
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.run_sa.email}"
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

resource "google_cloud_run_v2_service_iam_member" "build_manage_backend" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.jobnexus_service.name
  role     = "roles/run.developer"
  member   = "serviceAccount:${google_service_account.build_sa.email}"
}

resource "google_cloud_run_v2_service_iam_member" "build_manage_frontend" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.jobnexus_frontend.name
  role     = "roles/run.developer"
  member   = "serviceAccount:${google_service_account.build_sa.email}"
}

resource "google_service_account_iam_member" "build_act_as_run_sa" {
  service_account_id = google_service_account.run_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.build_sa.email}"
}

resource "google_cloud_run_v2_service_iam_member" "frontend_backend_access" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.jobnexus_service.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_project_iam_member" "run_firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.jobnexus_frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
