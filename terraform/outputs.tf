output "network_info" {
  description = "Network configuration information"
  value = {
    cidr        = var.network_cidr
    environment = var.environment
  }
}

output "instance_ips" {
  description = "IP addresses of deployed instances"
  value = concat(
    var.provider_type == "docker" ? module.docker[0].instance_ips : [],
    var.provider_type == "aws" ? module.aws[0].instance_ips : [],
    var.provider_type == "gcp" ? module.gcp[0].instance_ips : [],
    var.provider_type == "azure" ? module.azure[0].instance_ips : []
  )
}

output "monitoring_endpoints" {
  description = "Monitoring service endpoints"
  value = {
    prometheus = var.enable_monitoring ? "http://localhost:9090" : null
    grafana    = var.enable_monitoring ? "http://localhost:3000" : null
    kibana     = var.enable_monitoring ? "http://localhost:5601" : null
  }
  sensitive = false
}

output "honeypot_endpoints" {
  description = "Honeypot service endpoints"
  value = var.enable_honeypot ? merge(
    var.provider_type == "docker" ? module.docker[0].honeypot_endpoints : {},
    var.provider_type == "aws" ? module.aws[0].honeypot_endpoints : {},
    var.provider_type == "gcp" ? module.gcp[0].honeypot_endpoints : {},
    var.provider_type == "azure" ? module.azure[0].honeypot_endpoints : {}
  ) : {}
}

output "deployment_info" {
  description = "General deployment information"
  value = {
    provider    = var.provider_type
    environment = var.environment
    node_count  = var.node_count
    region      = var.region
  }
}
