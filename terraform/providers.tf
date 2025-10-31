# Provider configurations
# These must be in the root module, not in child modules

provider "docker" {
  # Docker provider configuration
  # Uses default socket connection
}

provider "aws" {
  region = var.region
  # AWS credentials should be provided via environment variables or AWS config
}

provider "google" {
  project = lookup(var.tags, "Project", "project-asylum")
  region  = var.region
  # GCP credentials should be provided via environment variables or gcloud config
}

provider "azurerm" {
  features {}
  # Azure credentials should be provided via environment variables or az cli config
}
