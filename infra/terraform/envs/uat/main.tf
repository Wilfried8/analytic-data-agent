provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

module "project_services" {
  source     = "../../modules/project_services"
  project_id = var.project_id
  services   = var.enabled_services
}

module "run_service_account" {
  source     = "../../modules/service_account"
  project_id = var.project_id
  account_id = var.run_service_account_id
  display_name = "Cloud Run service account (dev)"
  project_roles = [
    "roles/run.invoker",
    "roles/bigquery.dataViewer",
    "roles/bigquery.user",
    "roles/aiplatform.user",
    "roles/iam.serviceAccountUser",
    "roles/cloudaicompanion.user",
    "roles/aiplatform.user",
    "roles/owner"
  ]
}

module "cloud_run_service" {
  source          = "../../modules/cloud_run_service"
  project_id      = var.project_id
  region          = var.region
  service_name    = var.run_service_name
  image           = var.run_image
  service_account = module.run_service_account.email
  env_vars        = var.run_env_vars
  allow_unauthenticated = true
  labels = {
    environment = "dev"
  }
}
