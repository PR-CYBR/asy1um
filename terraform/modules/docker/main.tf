terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_network" "asylum_network" {
  name   = "asylum-${var.environment}"
  driver = "bridge"

  ipam_config {
    subnet = var.network_cidr
  }
}

resource "docker_volume" "asylum_data" {
  count = var.node_count
  name  = "asylum-data-${var.environment}-${count.index}"
}

resource "docker_image" "honeypot" {
  count        = var.enable_honeypot ? 1 : 0
  name         = "cowrie/cowrie:latest"
  keep_locally = true
}

resource "docker_container" "honeypot" {
  count = var.enable_honeypot ? var.node_count : 0
  name  = "asylum-honeypot-${var.environment}-${count.index}"
  image = docker_image.honeypot[0].image_id

  networks_advanced {
    name = docker_network.asylum_network.name
  }

  volumes {
    volume_name    = docker_volume.asylum_data[count.index].name
    container_path = "/cowrie/cowrie-git/var"
  }

  ports {
    internal = 2222
    external = 2222 + count.index
  }

  ports {
    internal = 2223
    external = 2223 + count.index
  }

  env = [
    "COWRIE_JSON_LOG_ENABLED=true",
    "COWRIE_OUTPUT_ELASTICSEARCH_ENABLED=true",
    "COWRIE_OUTPUT_ELASTICSEARCH_HOST=elasticsearch",
  ]

  restart = "unless-stopped"
}

resource "docker_image" "prometheus" {
  count        = var.enable_monitoring ? 1 : 0
  name         = "prom/prometheus:latest"
  keep_locally = true
}

resource "docker_container" "prometheus" {
  count = var.enable_monitoring ? 1 : 0
  name  = "asylum-prometheus-${var.environment}"
  image = docker_image.prometheus[0].image_id

  networks_advanced {
    name = docker_network.asylum_network.name
  }

  ports {
    internal = 9090
    external = 9090
  }

  restart = "unless-stopped"
}
