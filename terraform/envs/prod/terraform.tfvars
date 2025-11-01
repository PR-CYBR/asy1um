# Production Environment Configuration

environment       = "prod"
node_count        = 5
instance_type     = "t3.small"
network_cidr      = "10.1.0.0/16"
storage_size_gb   = 50
provider_type     = "docker"
region            = "us-east-1"
enable_monitoring = true
enable_honeypot   = true

tags = {
  Project     = "project-asylum"
  Environment = "prod"
  ManagedBy   = "terraform"
}
