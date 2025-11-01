output "instance_ips" {
  description = "Public IP addresses of honeypot instances"
  value       = var.enable_honeypot ? azurerm_public_ip.honeypot[*].ip_address : []
}

output "honeypot_endpoints" {
  description = "Honeypot service endpoints"
  value = var.enable_honeypot ? {
    for i in range(var.node_count) : "honeypot-${i}" => {
      ssh        = "${azurerm_public_ip.honeypot[i].ip_address}:22"
      telnet     = "${azurerm_public_ip.honeypot[i].ip_address}:23"
      private_ip = azurerm_network_interface.honeypot[i].private_ip_address
    }
  } : {}
}

output "vnet_id" {
  description = "Virtual Network ID"
  value       = azurerm_virtual_network.asylum.id
}

output "subnet_id" {
  description = "Subnet ID"
  value       = azurerm_subnet.asylum.id
}

output "monitoring_ip" {
  description = "Monitoring instance IP"
  value       = var.enable_monitoring ? azurerm_public_ip.monitoring[0].ip_address : null
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.asylum.name
}
