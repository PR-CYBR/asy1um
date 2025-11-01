# Docker module (default for local development)
module "docker" {
  source = "./modules/docker"
  count  = var.provider_type == "docker" ? 1 : 0

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

# AWS module
module "aws" {
  source = "./modules/aws"
  count  = var.provider_type == "aws" ? 1 : 0

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

# GCP module
module "gcp" {
  source = "./modules/gcp"
  count  = var.provider_type == "gcp" ? 1 : 0

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

# Azure module
module "azure" {
  source = "./modules/azure"
  count  = var.provider_type == "azure" ? 1 : 0

  environment       = var.environment
  node_count        = var.node_count
  instance_type     = var.instance_type
  network_cidr      = var.network_cidr
  storage_size_gb   = var.storage_size_gb
  region            = var.region
  tags              = var.tags
  enable_monitoring = var.enable_monitoring
  enable_honeypot   = var.enable_honeypot
  ssh_public_key    = var.ssh_public_key
}
