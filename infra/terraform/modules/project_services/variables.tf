variable "project_id" {
  description = "ID of the GCP project to enable services for."
  type        = string
}

variable "services" {
  description = "List of APIs to activate in the project."
  type        = list(string)
}
