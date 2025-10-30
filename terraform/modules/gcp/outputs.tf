output "instance_ips" {
  description = "Public IP addresses of honeypot instances"
  value       = var.enable_honeypot ? google_compute_instance.honeypot[*].network_interface[0].access_config[0].nat_ip : []
}

output "honeypot_endpoints" {
  description = "Honeypot service endpoints"
  value = var.enable_honeypot ? {
    for i, instance in google_compute_instance.honeypot : "honeypot-${i}" => {
      ssh        = "${instance.network_interface[0].access_config[0].nat_ip}:22"
      telnet     = "${instance.network_interface[0].access_config[0].nat_ip}:23"
      private_ip = instance.network_interface[0].network_ip
    }
  } : {}
}

output "vpc_id" {
  description = "VPC ID"
  value       = google_compute_network.asylum.id
}

output "subnet_id" {
  description = "Subnet ID"
  value       = google_compute_subnetwork.asylum.id
}

output "monitoring_ip" {
  description = "Monitoring instance IP"
  value       = var.enable_monitoring ? google_compute_instance.monitoring[0].network_interface[0].access_config[0].nat_ip : null
}
