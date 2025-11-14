variable "project_id" {
  description = "GCP project ID for the dev environment."
  type        = string
}

variable "region" {
  description = "Region where resources will be deployed."
  type        = string
  default     = "europe-west1"
}

variable "run_service_account_id" {
  description = "Service account ID (without domain) for Cloud Run."
  type        = string
  default     = "analytics-agent-run-dev"
}

variable "run_service_name" {
  description = "Cloud Run service name."
  type        = string
  default     = "analytics-agent-dev"
}

variable "run_image" {
  description = "Container image to deploy."
  type        = string
}

variable "run_env_vars" {
  description = "Environment variables for the Cloud Run container."
  type        = map(string)
  default     = {}
}

variable "enabled_services" {
  description = "Google APIs to enable in this project."
  type        = list(string)
  default = [
    "run.googleapis.com",
    "iam.googleapis.com",
    "geminidataanalytics.googleapis.com",
    "bigquery.googleapis.com",
  ]
}
