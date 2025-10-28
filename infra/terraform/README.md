# Terraform Infrastructure

This directory contains reusable Terraform modules and environment definitions to deploy
the Gemini Data Analytics agent workload on Google Cloud with Cloud Run.

## Modules

| Module | Purpose |
| ------ | ------- |
| `project_services` | Activates the required Google APIs (Cloud Run, Secret Manager, Gemini Data Analytics, BigQuery, etc.) for a project. |
| `service_account` | Provisions a dedicated service account and attaches IAM roles the workload needs (Cloud Run invocation, BigQuery data viewer, Gemini Data Analytics access). |
| `secret_manager_secret` | Manages a Secret Manager secret, optionally seeding an initial value and granting access to service accounts. |
| `cloud_run_service` | Deploys a Cloud Run v2 service with configurable container image, resources, environment variables, ingress, and public access. |

Each module is self-contained so it can be composed inside per-environment Terraform configurations.

## Environment Layout

Create environment folders under `envs/` (e.g., `staging`, `production`) containing:

```
envs/<env>/
  main.tf
  variables.tf
  outputs.tf
  versions.tf
  terraform.tfvars         # optional, holds environment-specific values
```

Within `main.tf`, instantiate the modules, for example:

```hcl
module "services" {
  source     = "../modules/project_services"
  project_id = var.project_id
  services   = [
    "run.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com",
    "geminidataanalytics.googleapis.com",
    "bigquery.googleapis.com",
  ]
}

module "run_service_account" {
  source      = "../modules/service_account"
  project_id  = var.project_id
  account_id  = var.run_service_account_id
  project_roles = [
    "roles/run.invoker",
    "roles/bigquery.dataViewer",
    "roles/genaihq.dataAgentUser",
  ]
}

module "cloud_run" {
  source          = "../modules/cloud_run_service"
  project_id      = var.project_id
  region          = var.region
  service_name    = var.run_service_name
  image           = var.run_image
  service_account = module.run_service_account.email
  env_vars        = var.run_env_vars
}
```

## Usage

1. Authenticate with Google Cloud (`gcloud auth application-default login`) and set the correct project.
2. Navigate to the environment folder, run `terraform init`.
3. Execute `terraform plan` with the required variables (project, region, image, etc.).
4. Apply after review.
5. Store Terraform state in a remote backend (e.g., Cloud Storage) for team use.
