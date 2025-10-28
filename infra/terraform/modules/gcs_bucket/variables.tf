variable "project_id" {
    description = "The ID of the GCP project where the bucket will be created."
    type = string
}

variable "bucket_name" {
    description = "value"
    type = string
}

variable "location" {
  description = "The location/region for the bucket (e.g., EU, US, europe-west1)."
  type        = string
  default     = "EU"
}

variable "storage_class" {
  description = "The storage class for the bucket (STANDARD, NEARLINE, COLDLINE, ARCHIVE)."
  type        = string
  default     = "STANDARD"
}

variable "force_destroy" {
  description = "If true, delete the bucket even if it contains objects."
  type        = bool
  default     = false
}

variable "versioning_enabled" {
  description = "If true, enables object versioning on the bucket."
  type        = bool
  default     = false
}

variable "labels" {
  description = "Key-value pairs of labels to assign to the bucket."
  type        = map(string)
  default     = {}
}