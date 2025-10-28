variable "project_id" {
  type        = string
  description = "The GCP project ID where the repository will be created."
}

variable "region" {
  type        = string
  description = "Region of the Artifact Registry repository."
  default     = "europe-west1"
}

variable "repository_name" {
  type        = string
  description = "Repository ID (name of the Artifact Registry repo)."
}

variable "description" {
  type        = string
  description = "Repository description."
  default     = "Docker images repository managed by Terraform."
}

variable "labels" {
  type        = map(string)
  description = "Labels applied to the repository."
  default = {
    env = "dev"
  }
}
