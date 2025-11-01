variable "environment" {
  description = "Environment name"
  type        = string
}

variable "node_count" {
  description = "Number of nodes"
  type        = number
}

variable "instance_type" {
  description = "Azure VM size"
  type        = string
}

variable "network_cidr" {
  description = "VNet CIDR"
  type        = string
}

variable "storage_size_gb" {
  description = "Disk size in GB"
  type        = number
}

variable "region" {
  description = "Azure region"
  type        = string
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
}

variable "enable_monitoring" {
  description = "Enable monitoring"
  type        = bool
}

variable "enable_honeypot" {
  description = "Enable honeypot"
  type        = bool
}

variable "ssh_public_key" {
  description = "SSH public key for Azure VMs"
  type        = string
  default     = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7... # Replace with actual key or pass via variable"
}
