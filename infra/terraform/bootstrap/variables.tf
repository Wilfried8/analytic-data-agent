variable "project_id" {
  type        = string
  description = "GCP project id"
}

variable "region" {
  type        = string
  description = "Region (e.g., europe-west1)"
}

variable "state_bucket_name" {
  type        = string
  description = "Unique name for the Terraform state bucket"
}

variable "environment" {
  type        = string
  description = "Environment tag (dev, prod...)"
  default     = "dev"
}
