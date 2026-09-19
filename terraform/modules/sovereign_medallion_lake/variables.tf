variable "project_id" {
  description = "The GCP Project ID where the sovereign data lake bucket will be created."
  type        = string
}

variable "entity_id" {
  description = "The sovereign entity identifier (e.g. ppac, niti_aayog, pngrb)."
  type        = string
  default     = "ppac"
}

variable "region" {
  description = "GCP Region for the bucket (default: asia-south1 Mumbai)."
  type        = string
  default     = "asia-south1"
}

variable "retention_years" {
  description = "Statutory data retention period in years for Zone 1 Raw Inbox."
  type        = number
  default     = 5
}
