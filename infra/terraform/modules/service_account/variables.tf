variable "project_id" {
  description = "ID of the GCP project where the service account lives."
  type        = string
}

variable "account_id" {
  description = "Service account ID (without domain)."
  type        = string
}

variable "display_name" {
  description = "Display name of the service account."
  type        = string
  default     = "Cloud Run service account"
}

variable "project_roles" {
  description = "List of IAM roles to grant at the project level."
  type        = list(string)
  default     = []
}
