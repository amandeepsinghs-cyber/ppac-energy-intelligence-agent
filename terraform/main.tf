# Root Terraform deployment for PPAC and Sovereign Entities

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type    = string
  default = "og-enterprise-analytics-prod"
}

variable "region" {
  type    = string
  default = "asia-south1"
}

# 1. PPAC Sovereign Data Lake Bucket
module "ppac_data_lake" {
  source     = "./modules/sovereign_medallion_lake"
  project_id = var.project_id
  entity_id  = "ppac"
  region     = var.region
}

# 2. Template ready for other Sovereign Entities (e.g. NITI Aayog, PNGRB)
# module "niti_aayog_data_lake" {
#   source     = "./modules/sovereign_medallion_lake"
#   project_id = var.project_id
#   entity_id  = "niti-aayog"
#   region     = var.region
# }
