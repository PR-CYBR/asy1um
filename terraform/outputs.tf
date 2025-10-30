output "network_info" {
  description = "Network configuration information"
  value = {
    cidr        = var.network_cidr
    environment = var.environment
  }
}

output "instance_ips" {
  description = "IP addresses of deployed instances"
  value       = module.infrastructure.instance_ips
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
  value       = var.enable_honeypot ? module.infrastructure.honeypot_endpoints : {}
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
