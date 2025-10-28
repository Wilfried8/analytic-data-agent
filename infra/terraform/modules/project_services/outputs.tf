output "enabled_services" {
  description = "List of services that were enabled."
  value       = [for s in google_project_service.this : s.service]
}
