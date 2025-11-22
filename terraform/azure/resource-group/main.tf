# Resource Group Module

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.azure_region

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}
