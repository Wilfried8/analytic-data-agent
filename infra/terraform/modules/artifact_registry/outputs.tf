output "repository_id" {
  value       = google_artifact_registry_repository.this.repository_id
  description = "ID of the created Artifact Registry repository."
}

output "repository_url" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.this.repository_id}"
  description = "URL to push/pull images."
}
