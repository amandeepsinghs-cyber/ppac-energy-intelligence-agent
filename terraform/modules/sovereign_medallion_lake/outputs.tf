output "bucket_name" {
  description = "The name of the created sovereign data lake bucket."
  value       = google_storage_bucket.sovereign_lake.name
}

output "bucket_url" {
  description = "The gs:// URL of the sovereign data lake bucket."
  value       = google_storage_bucket.sovereign_lake.url
}
