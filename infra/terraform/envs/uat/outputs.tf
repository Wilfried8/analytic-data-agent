output "cloud_run_service_url" {
  description = "Deployed Cloud Run service URL."
  value       = module.cloud_run_service.url
}

output "service_account_email" {
  description = "Email of the Cloud Run service account."
  value       = module.run_service_account.email
}
