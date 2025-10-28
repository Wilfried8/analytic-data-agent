output "service_id" {
  description = "Full resource name of the Cloud Run service."
  value       = google_cloud_run_v2_service.this.name
}

output "url" {
  description = "Default URL of the deployed Cloud Run service."
  value       = google_cloud_run_v2_service.this.uri
}
