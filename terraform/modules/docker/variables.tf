variable "environment" {
  description = "Environment name"
  type        = string
}

variable "node_count" {
  description = "Number of nodes"
  type        = number
}

variable "instance_type" {
  description = "Instance type (not used for Docker)"
  type        = string
}

variable "network_cidr" {
  description = "Network CIDR"
  type        = string
}

variable "storage_size_gb" {
  description = "Storage size in GB"
  type        = number
}

variable "region" {
  description = "Region (not used for Docker)"
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
