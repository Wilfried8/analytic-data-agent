variable "project_id" {
  description = "ID of the GCP project."
  type        = string
}

variable "region" {
  description = "Region where Cloud Run service is deployed."
  type        = string
}

variable "service_name" {
  description = "Name of the Cloud Run service."
  type        = string
}

variable "image" {
  description = "Container image to deploy."
  type        = string
}

variable "service_account" {
  description = "Service account email used by Cloud Run."
  type        = string
}

variable "env_vars" {
  description = "Environment variables injected into the container."
  type        = map(string)
  default     = {}
}

variable "labels" {
  description = "Labels applied to the Cloud Run revision."
  type        = map(string)
  default     = {}
}

variable "cpu" {
  description = "CPU limit for the container (e.g., 1, 2)."
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory limit for the container (e.g., 512Mi, 1Gi)."
  type        = string
  default     = "512Mi"
}

variable "port" {
  description = "Container port exposed by the application."
  type        = number
  default     = 8080
}

variable "timeout_seconds" {
  description = "Request timeout in seconds."
  type        = number
  default     = 300
}

variable "max_concurrency" {
  description = "Maximum number of concurrent requests per container instance."
  type        = number
  default     = 80
}

variable "ingress" {
  description = "Ingress setting (INGRESS_TRAFFIC_ALL, INTERNAL_ONLY, etc.)."
  type        = string
  default     = "INGRESS_TRAFFIC_ALL"
}

variable "allow_unauthenticated" {
  description = "Grant public invoker access to the service."
  type        = bool
  default     = false
}
