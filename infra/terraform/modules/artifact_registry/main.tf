resource "google_artifact_registry_repository" "this" {
  provider          = google
  project           = var.project_id
  location          = var.region
  repository_id     = var.repository_name
  description       = var.description
  format            = "DOCKER"

  labels = var.labels
}
