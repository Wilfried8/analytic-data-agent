output "email" {
  description = "Email address of the created service account."
  value       = google_service_account.this.email
}

output "name" {
  description = "Resource name of the service account."
  value       = google_service_account.this.name
}
