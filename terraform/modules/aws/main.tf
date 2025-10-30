terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_vpc" "asylum" {
  cidr_block           = var.network_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.tags, {
    Name        = "asylum-vpc-${var.environment}"
    Environment = var.environment
  })
}

resource "aws_subnet" "asylum" {
  vpc_id                  = aws_vpc.asylum.id
  cidr_block              = cidrsubnet(var.network_cidr, 8, 1)
  map_public_ip_on_launch = true
  availability_zone       = "${var.region}a"

  tags = merge(var.tags, {
    Name        = "asylum-subnet-${var.environment}"
    Environment = var.environment
  })
}

resource "aws_internet_gateway" "asylum" {
  vpc_id = aws_vpc.asylum.id

  tags = merge(var.tags, {
    Name        = "asylum-igw-${var.environment}"
    Environment = var.environment
  })
}

resource "aws_route_table" "asylum" {
  vpc_id = aws_vpc.asylum.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.asylum.id
  }

  tags = merge(var.tags, {
    Name        = "asylum-rt-${var.environment}"
    Environment = var.environment
  })
}

resource "aws_route_table_association" "asylum" {
  subnet_id      = aws_subnet.asylum.id
  route_table_id = aws_route_table.asylum.id
}

resource "aws_security_group" "honeypot" {
  name        = "asylum-honeypot-${var.environment}"
  description = "Security group for honeypot instances"
  vpc_id      = aws_vpc.asylum.id

  ingress {
    description = "SSH honeypot"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Telnet honeypot"
    from_port   = 23
    to_port     = 23
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name        = "asylum-honeypot-sg-${var.environment}"
    Environment = var.environment
  })
}

resource "aws_instance" "honeypot" {
  count         = var.enable_honeypot ? var.node_count : 0
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.asylum.id

  vpc_security_group_ids = [aws_security_group.honeypot.id]

  root_block_device {
    volume_size = var.storage_size_gb
    volume_type = "gp3"
  }

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y docker.io docker-compose
              systemctl enable docker
              systemctl start docker
              docker run -d --name cowrie -p 22:2222 -p 23:2223 cowrie/cowrie:latest
              EOF

  tags = merge(var.tags, {
    Name        = "asylum-honeypot-${var.environment}-${count.index}"
    Environment = var.environment
    Role        = "honeypot"
  })
}

resource "aws_instance" "monitoring" {
  count         = var.enable_monitoring ? 1 : 0
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.asylum.id

  vpc_security_group_ids = [aws_security_group.honeypot.id]

  root_block_device {
    volume_size = var.storage_size_gb * 2
    volume_type = "gp3"
  }

  tags = merge(var.tags, {
    Name        = "asylum-monitoring-${var.environment}"
    Environment = var.environment
    Role        = "monitoring"
  })
}
