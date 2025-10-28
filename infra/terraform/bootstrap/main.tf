terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "state_bucket" {
  source       = "../modules/gcs_bucket"
  project_id   = var.project_id
  bucket_name  = var.state_bucket_name
  location     = var.region
  storage_class      = "STANDARD"
  versioning_enabled = true
  labels = {
    purpose      = "terraform-state"
    environment  = var.environment
  }
}
