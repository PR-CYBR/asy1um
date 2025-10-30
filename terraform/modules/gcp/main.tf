terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.tags["Project"]
  region  = var.region
}

data "google_compute_image" "ubuntu" {
  family  = "ubuntu-2204-lts"
  project = "ubuntu-os-cloud"
}

resource "google_compute_network" "asylum" {
  name                    = "asylum-vpc-${var.environment}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "asylum" {
  name          = "asylum-subnet-${var.environment}"
  ip_cidr_range = var.network_cidr
  region        = var.region
  network       = google_compute_network.asylum.id
}

resource "google_compute_firewall" "honeypot_ssh" {
  name    = "asylum-honeypot-ssh-${var.environment}"
  network = google_compute_network.asylum.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["honeypot"]
}

resource "google_compute_firewall" "honeypot_telnet" {
  name    = "asylum-honeypot-telnet-${var.environment}"
  network = google_compute_network.asylum.name

  allow {
    protocol = "tcp"
    ports    = ["23"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["honeypot"]
}

resource "google_compute_firewall" "honeypot_http" {
  name    = "asylum-honeypot-http-${var.environment}"
  network = google_compute_network.asylum.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["honeypot"]
}

resource "google_compute_instance" "honeypot" {
  count        = var.enable_honeypot ? var.node_count : 0
  name         = "asylum-honeypot-${var.environment}-${count.index}"
  machine_type = var.instance_type
  zone         = "${var.region}-a"

  boot_disk {
    initialize_params {
      image = data.google_compute_image.ubuntu.self_link
      size  = var.storage_size_gb
      type  = "pd-standard"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.asylum.id

    access_config {
      // Ephemeral public IP
    }
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose
    systemctl enable docker
    systemctl start docker
    docker run -d --name cowrie -p 22:2222 -p 23:2223 cowrie/cowrie:latest
  EOF

  tags = ["honeypot"]

  labels = merge(var.tags, {
    environment = var.environment
    role        = "honeypot"
  })
}

resource "google_compute_instance" "monitoring" {
  count        = var.enable_monitoring ? 1 : 0
  name         = "asylum-monitoring-${var.environment}"
  machine_type = var.instance_type
  zone         = "${var.region}-a"

  boot_disk {
    initialize_params {
      image = data.google_compute_image.ubuntu.self_link
      size  = var.storage_size_gb * 2
      type  = "pd-standard"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.asylum.id

    access_config {
      // Ephemeral public IP
    }
  }

  tags = ["monitoring"]

  labels = merge(var.tags, {
    environment = var.environment
    role        = "monitoring"
  })
}
