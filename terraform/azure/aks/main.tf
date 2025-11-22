# AKS Cluster Module

resource "azurerm_kubernetes_cluster" "main" {
  name                = var.cluster_name
  location            = var.azure_region
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.cluster_name}-dns"
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name                = "system"
    vm_size             = var.node_pools.system.vm_size
    node_count          = var.node_pools.system.node_count
    min_count           = var.node_pools.system.min_count
    max_count           = var.node_pools.system.max_count
    enable_auto_scaling = var.node_pools.system.enable_auto_scaling
    max_pods            = var.node_pools.system.max_pods
    vnet_subnet_id      = var.subnet_id
    type                = "VirtualMachineScaleSets"

    node_labels = {
      "workload" = "system"
    }

    tags = merge(
      var.tags,
      {
        Environment = var.environment
        NodePool    = "system"
      }
    )
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "calico"
    load_balancer_sku = "standard"
    # Service CIDR for Kubernetes services (172.16.0.0/16 to avoid conflicts with common private networks)
    service_cidr   = "172.16.0.0/16"
    # DNS service IP must be within the service CIDR range
    dns_service_ip = "172.16.0.10"
  }

  dynamic "oms_agent" {
    for_each = var.log_analytics_workspace_id != null ? [1] : []
    content {
      log_analytics_workspace_id = var.log_analytics_workspace_id
    }
  }

  azure_policy_enabled = true

  tags = merge(
    var.tags,
    {
      Environment = var.environment
    }
  )
}

# AI Workload Node Pool
resource "azurerm_kubernetes_cluster_node_pool" "ai_workload" {
  name                  = "aiworkload"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = var.node_pools.ai_workload.vm_size
  node_count            = var.node_pools.ai_workload.node_count
  min_count             = var.node_pools.ai_workload.min_count
  max_count             = var.node_pools.ai_workload.max_count
  enable_auto_scaling   = var.node_pools.ai_workload.enable_auto_scaling
  max_pods              = var.node_pools.ai_workload.max_pods
  vnet_subnet_id        = var.subnet_id

  node_labels = {
    "workload" = "ai"
  }

  tags = merge(
    var.tags,
    {
      Environment = var.environment
      NodePool    = "ai-workload"
    }
  )
}
