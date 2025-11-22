variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "azure_region" {
  description = "Azure region for the virtual network"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = list(string)
}

variable "subnet_address_prefix" {
  description = "Address prefix for AKS subnet"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
