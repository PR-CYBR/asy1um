# Development Environment Configuration

environment       = "dev"
node_count        = 2
instance_type     = "t3.micro"
network_cidr      = "10.0.0.0/16"
storage_size_gb   = 20
provider_type     = "docker"
region            = "us-east-1"
enable_monitoring = true
enable_honeypot   = true

tags = {
  Project     = "project-asylum"
  Environment = "dev"
  ManagedBy   = "terraform"
}
