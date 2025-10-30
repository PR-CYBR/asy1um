terraform {
  required_version = ">= 1.0"
  
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

module "infrastructure" {
  source = "./modules/${var.provider_type}"

  environment       = var.environment
  node_count        = var.node_count
  instance_type     = var.instance_type
  network_cidr      = var.network_cidr
  storage_size_gb   = var.storage_size_gb
  region            = var.region
  tags              = var.tags
  enable_monitoring = var.enable_monitoring
  enable_honeypot   = var.enable_honeypot
}
