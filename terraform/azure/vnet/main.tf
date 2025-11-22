# Virtual Network Module

resource "azurerm_virtual_network" "main" {
  name                = "${var.environment}-aks-vnet"
  location            = var.azure_region
  resource_group_name = var.resource_group_name
  address_space       = var.vnet_address_space

  tags = merge(
    var.tags,
    {
      Environment = var.environment
      Purpose     = "AKS Networking"
    }
  )
}

resource "azurerm_subnet" "aks" {
  name                 = "${var.environment}-aks-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_address_prefix]

  # Enable service endpoints
  service_endpoints = [
    "Microsoft.Storage",
    "Microsoft.KeyVault",
    "Microsoft.ContainerRegistry",
    "Microsoft.Sql"
  ]
}

resource "azurerm_network_security_group" "aks" {
  name                = "${var.environment}-aks-nsg"
  location            = var.azure_region
  resource_group_name = var.resource_group_name

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

resource "azurerm_subnet_network_security_group_association" "aks" {
  subnet_id                 = azurerm_subnet.aks.id
  network_security_group_id = azurerm_network_security_group.aks.id
}
