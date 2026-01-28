# The Google Cloud Project ID where resources will be deployed
variable "project_id" {
  description = "Project ID"
  type        = string
  default     = "jobnexus-479520"
}

# The default GCP region for resources
variable "region" {
  description = "Default region"
  type        = string
  default     = "europe-west1"
}

variable "jobs" {
  description = "The jobs to track daily"
  type        = set(string)
  default     = [
    "DevOps",
    "DevSecOps",
    "SRE",
    "Ingenieur-Cloud",
    "Ingenieur-Systeme",
    "Ingenieur-Reseaux",
    "Cybersecurity",
    "Cloud-Computing"
  ]
}
