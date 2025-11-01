# Provider configurations
# These must be in the root module, not in child modules

provider "docker" {
  # Docker provider configuration
  # Uses default socket connection
}

provider "aws" {
  region     = var.region
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  # AWS credentials should be provided via environment variables or AWS config
}

provider "google" {
  project = lookup(var.tags, "Project", "project-asylum")
  region  = var.region
  # GCP credentials should be provided via environment variables or gcloud config
  # For CI/CD without credentials, set GOOGLE_APPLICATION_CREDENTIALS or use skip flags
}

provider "azurerm" {
  features {}
  skip_provider_registration = true
  # Azure credentials should be provided via environment variables or az cli config
}
