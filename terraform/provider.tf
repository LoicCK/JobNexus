# Configure the main Google Cloud provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Configure the Google Beta provider (needed for API Gateway)
provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Configure Terraform to store the state file in a Google Cloud Storage bucket
terraform {
  backend "gcs" {
    bucket  = "tf-state-jobnexus-479520"
    prefix  = "terraform/state"
  }
}