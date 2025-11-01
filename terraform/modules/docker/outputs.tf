output "instance_ips" {
  description = "IP addresses of Docker containers"
  value = var.enable_honeypot ? [
    for i in range(var.node_count) : "172.17.0.${i + 2}"
  ] : []
}

output "honeypot_endpoints" {
  description = "Honeypot service endpoints"
  value = var.enable_honeypot ? {
    for i in range(var.node_count) : "honeypot-${i}" => {
      ssh    = "localhost:${2222 + i}"
      telnet = "localhost:${2223 + i}"
    }
  } : {}
}

output "network_id" {
  description = "Docker network ID"
  value       = docker_network.asylum_network.id
}

output "network_name" {
  description = "Docker network name"
  value       = docker_network.asylum_network.name
}
