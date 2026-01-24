provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

terraform {
  backend "gcs" {
    bucket  =  "tf-state-jobnexus-479520"
    prefix  = "terraform/state"
  }
}