# Terraform Module: Sovereign Medallion Data Lake Bucket Auto-Provisioning

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# 1. Primary Sovereign Cloud Storage Bucket with Uniform Access & Versioning
resource "google_storage_bucket" "sovereign_lake" {
  name                        = "og-sovereign-${var.entity_id}-data"
  project                     = var.project_id
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age        = 90
      with_state = "ANY"
      matches_prefix = ["1_raw_inbox/"]
    }
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
    condition {
      age        = 365
      with_state = "ANY"
      matches_prefix = ["1_raw_inbox/"]
    }
  }

  labels = {
    governance_domain = "sovereign_regulatory"
    entity_id         = var.entity_id
    architecture      = "medallion_4tier"
    managed_by        = "terraform"
  }
}

# 2. Mandatory Medallion Zones & PSU Submissions Initializer
locals {
  zone_markers = toset([
    # Zone 1: Raw Inbox (API & PSU Ingestion)
    "1_raw_inbox/psu_submissions/iocl/.zone_keep",
    "1_raw_inbox/psu_submissions/bpcl/.zone_keep",
    "1_raw_inbox/psu_submissions/hpcl/.zone_keep",
    "1_raw_inbox/psu_submissions/ongc/.zone_keep",
    "1_raw_inbox/psu_submissions/gail/.zone_keep",
    "1_raw_inbox/psu_submissions/private_operators/.zone_keep",
    "1_raw_inbox/market_feeds_api/.zone_keep",
    "1_raw_inbox/government_dispatches/.zone_keep",
    "1_raw_inbox/official_publications/.zone_keep",
    "1_raw_inbox/text_commentary/.zone_keep",

    # Zone 2: Curated Canonical Parquet / JSON
    "2_curated/.zone_keep",

    # Zone 3: Publications & Executive Artifacts
    "3_artifacts/approved/.zone_keep",
    "3_artifacts/draft/.zone_keep",
    "3_artifacts/charts/.zone_keep",

    # Zone 4: Exceptions & Audit Ledger
    "4_quarantine/corrupted_inputs/.zone_keep",
    "4_quarantine/variance_exceptions/.zone_keep",
    "4_quarantine/audit_resolutions/.zone_keep",
  ])
}

resource "google_storage_bucket_object" "medallion_skeleton" {
  for_each = local.zone_markers
  name     = each.value
  content  = "Sovereign Medallion Zone Initialized by Terraform"
  bucket   = google_storage_bucket.sovereign_lake.name
}
