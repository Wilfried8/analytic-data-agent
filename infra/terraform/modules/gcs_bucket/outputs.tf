output "bucket_name" {
  description = "The name of the bucket created."
  value       = google_storage_bucket.this.name
}

output "bucket_url" {
  description = "The public URL of the bucket."
  value       = google_storage_bucket.this.url
}

output "self_link" {
  description = "The internal self link of the bucket in GCP."
  value       = google_storage_bucket.this.self_link
}
