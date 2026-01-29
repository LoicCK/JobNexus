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

variable "default_latitude" {
  description = "Default latitude for job search (Paris)"
  type        = string
  default     = "48.8566"
}

variable "default_longitude" {
  description = "Default longitude for job search (Paris)"
  type        = string
  default     = "2.3522"
}

variable "default_radius" {
  description = "Search radius in km"
  type        = string
  default     = "30"
}

variable "default_insee" {
  description = "INSEE code for location"
  type        = string
  default     = "75056"
}
