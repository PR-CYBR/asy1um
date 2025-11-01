terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

resource "azurerm_resource_group" "asylum" {
  name     = "asylum-rg-${var.environment}"
  location = var.region
  tags     = var.tags
}

resource "azurerm_virtual_network" "asylum" {
  name                = "asylum-vnet-${var.environment}"
  address_space       = [var.network_cidr]
  location            = azurerm_resource_group.asylum.location
  resource_group_name = azurerm_resource_group.asylum.name
  tags                = var.tags
}

resource "azurerm_subnet" "asylum" {
  name                 = "asylum-subnet-${var.environment}"
  resource_group_name  = azurerm_resource_group.asylum.name
  virtual_network_name = azurerm_virtual_network.asylum.name
  address_prefixes     = [cidrsubnet(var.network_cidr, 8, 1)]
}

resource "azurerm_network_security_group" "honeypot" {
  name                = "asylum-honeypot-nsg-${var.environment}"
  location            = azurerm_resource_group.asylum.location
  resource_group_name = azurerm_resource_group.asylum.name

  security_rule {
    name                       = "SSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "Telnet"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "23"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "HTTP"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = var.tags
}

resource "azurerm_public_ip" "honeypot" {
  count               = var.enable_honeypot ? var.node_count : 0
  name                = "asylum-honeypot-pip-${var.environment}-${count.index}"
  location            = azurerm_resource_group.asylum.location
  resource_group_name = azurerm_resource_group.asylum.name
  allocation_method   = "Static"
  tags                = var.tags
}

resource "azurerm_network_interface" "honeypot" {
  count               = var.enable_honeypot ? var.node_count : 0
  name                = "asylum-honeypot-nic-${var.environment}-${count.index}"
  location            = azurerm_resource_group.asylum.location
  resource_group_name = azurerm_resource_group.asylum.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.asylum.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.honeypot[count.index].id
  }

  tags = var.tags
}

resource "azurerm_network_interface_security_group_association" "honeypot" {
  count                     = var.enable_honeypot ? var.node_count : 0
  network_interface_id      = azurerm_network_interface.honeypot[count.index].id
  network_security_group_id = azurerm_network_security_group.honeypot.id
}

resource "azurerm_linux_virtual_machine" "honeypot" {
  count               = var.enable_honeypot ? var.node_count : 0
  name                = "asylum-honeypot-${var.environment}-${count.index}"
  location            = azurerm_resource_group.asylum.location
  resource_group_name = azurerm_resource_group.asylum.name
  size                = var.instance_type
  admin_username      = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.honeypot[count.index].id,
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb         = var.storage_size_gb
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  custom_data = base64encode(<<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose
    systemctl enable docker
    systemctl start docker
    docker run -d --name cowrie -p 22:2222 -p 23:2223 cowrie/cowrie:latest
  EOF
  )

  tags = merge(var.tags, {
    Role = "honeypot"
  })
}

resource "azurerm_public_ip" "monitoring" {
  count               = var.enable_monitoring ? 1 : 0
  name                = "asylum-monitoring-pip-${var.environment}"
  location            = azurerm_resource_group.asylum.location
  resource_group_name = azurerm_resource_group.asylum.name
  allocation_method   = "Static"
  tags                = var.tags
}

resource "azurerm_network_interface" "monitoring" {
  count               = var.enable_monitoring ? 1 : 0
  name                = "asylum-monitoring-nic-${var.environment}"
  location            = azurerm_resource_group.asylum.location
  resource_group_name = azurerm_resource_group.asylum.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.asylum.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.monitoring[0].id
  }

  tags = var.tags
}

resource "azurerm_linux_virtual_machine" "monitoring" {
  count               = var.enable_monitoring ? 1 : 0
  name                = "asylum-monitoring-${var.environment}"
  location            = azurerm_resource_group.asylum.location
  resource_group_name = azurerm_resource_group.asylum.name
  size                = var.instance_type
  admin_username      = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.monitoring[0].id,
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
    disk_size_gb         = var.storage_size_gb * 2
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  tags = merge(var.tags, {
    Role = "monitoring"
  })
}
