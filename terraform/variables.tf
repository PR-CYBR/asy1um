variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
  default     = "dev"
}

variable "node_count" {
  description = "Number of honeypot nodes to deploy"
  type        = number
  default     = 3
}

variable "instance_type" {
  description = "Instance type for cloud deployments"
  type        = string
  default     = "t3.micro"
}

variable "network_cidr" {
  description = "CIDR block for the network"
  type        = string
  default     = "10.0.0.0/16"
}

variable "storage_size_gb" {
  description = "Storage size in GB for each node"
  type        = number
  default     = 20
}

variable "provider_type" {
  description = "Infrastructure provider (docker, proxmox, aws, gcp, azure)"
  type        = string
  default     = "docker"
}

variable "region" {
  description = "Cloud provider region"
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Project = "project-asylum"
  }
}

variable "enable_monitoring" {
  description = "Enable monitoring stack"
  type        = bool
  default     = true
}

variable "enable_honeypot" {
  description = "Enable honeypot deployment"
  type        = bool
  default     = true
}
