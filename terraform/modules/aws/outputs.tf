output "instance_ips" {
  description = "Public IP addresses of honeypot instances"
  value       = var.enable_honeypot ? aws_instance.honeypot[*].public_ip : []
}

output "honeypot_endpoints" {
  description = "Honeypot service endpoints"
  value = var.enable_honeypot ? {
    for i, instance in aws_instance.honeypot : "honeypot-${i}" => {
      ssh        = "${instance.public_ip}:22"
      telnet     = "${instance.public_ip}:23"
      private_ip = instance.private_ip
    }
  } : {}
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.asylum.id
}

output "subnet_id" {
  description = "Subnet ID"
  value       = aws_subnet.asylum.id
}

output "monitoring_ip" {
  description = "Monitoring instance IP"
  value       = var.enable_monitoring ? aws_instance.monitoring[0].public_ip : null
}
