# Azure Infrastructure for AI DevOps

This Terraform configuration deploys a complete Azure infrastructure for running AI workloads with comprehensive monitoring and observability using Azure Monitor and Application Insights.

## Architecture

The infrastructure includes:
- **Resource Group**: Logical container for Azure resources
- **AKS Cluster**: Managed Kubernetes cluster for AI workloads
- **Virtual Network**: VNet with subnets for cluster nodes
- **Application Insights**: Application performance monitoring and logging
- **Log Analytics Workspace**: Centralized logging and analytics
- **Azure Monitor**: Metrics, alerts, and dashboards
- **Container Insights**: Container and cluster monitoring

## Prerequisites

- Azure subscription
- Azure CLI installed and configured
- Terraform >= 1.0
- kubectl
- helm (optional)

## Quick Start

### 1. Install Azure CLI

```bash
# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows
# Download from https://aka.ms/installazurecliwindows
```

### 2. Login to Azure

```bash
az login
az account set --subscription "your-subscription-id"
```

### 3. Initialize Terraform

```bash
cd terraform/azure
terraform init
```

### 4. Review and Customize Variables

Create a `terraform.tfvars` file:

```hcl
azure_region        = "eastus"
environment         = "dev"
resource_group_name = "ai-devops-rg"
cluster_name        = "ai-devops-aks"
kubernetes_version  = "1.28"

node_pools = {
  system = {
    vm_size             = "Standard_D4s_v3"
    node_count          = 3
    min_count           = 2
    max_count           = 10
    enable_auto_scaling = true
  }
  ai_workload = {
    vm_size             = "Standard_D8s_v3"
    node_count          = 3
    min_count           = 2
    max_count           = 20
    enable_auto_scaling = true
  }
}

application_insights_retention_days = 90
log_analytics_retention_days        = 90
```

### 5. Plan the Deployment

```bash
terraform plan -out=tfplan
```

### 6. Apply the Configuration

```bash
terraform apply tfplan
```

This will take approximately 10-15 minutes to create all resources.

### 7. Configure kubectl

```bash
az aks get-credentials \
  --resource-group ai-devops-rg \
  --name ai-devops-aks
```

### 8. Verify Cluster Access

```bash
kubectl get nodes
kubectl get pods --all-namespaces
```

## Module Structure

```
azure/
├── main.tf                    # Root module configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── README.md                  # This file
├── resource-group/            # Resource group module
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── vnet/                      # Virtual network module
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── aks/                       # AKS cluster module
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
└── monitoring/                # Azure Monitor and App Insights
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

## Features

### Resource Group
- Centralized resource management
- Consistent tagging for cost tracking
- Regional deployment flexibility

### Virtual Network (VNet)
- Isolated network for AKS cluster
- Subnet for AKS nodes
- Network security groups
- Service endpoints for Azure services

### AKS Cluster
- Managed Kubernetes control plane
- System node pool for cluster services
- AI workload node pool for applications
- Managed identity for secure access
- Azure CNI networking
- Auto-scaling capabilities
- Azure AD integration

### Node Pools
- **System Pool**: Critical cluster services (CoreDNS, metrics-server)
- **AI Workload Pool**: Application workloads with auto-scaling
- Configurable VM sizes and scaling parameters
- Taints and labels for workload separation

### Application Insights
- Distributed tracing
- Performance monitoring
- Custom metrics and events
- Log correlation
- Live metrics stream
- Failure analysis

### Log Analytics Workspace
- Centralized log aggregation
- Kusto Query Language (KQL) queries
- Log retention policies
- Integration with Azure Monitor

### Container Insights
- Node and pod metrics
- Container logs
- Performance counters
- Kubernetes events
- Workload monitoring

### Azure Monitor
- Custom metric collection
- Alert rules for:
  - High inference latency
  - High error rate
  - Resource utilization
  - Cost thresholds
- Action groups for notifications
- Dashboards for visualization

## Outputs

After deployment, Terraform will output:

```
resource_group_name              = "ai-devops-rg"
aks_cluster_name                 = "ai-devops-aks"
aks_cluster_endpoint             = "https://ai-devops-aks-xxxxx.hcp.eastus.azmk8s.io"
application_insights_key         = "xxxxx-xxxxx-xxxxx"
application_insights_connection_string = "InstrumentationKey=xxxxx;IngestionEndpoint=https://eastus-1.in.applicationinsights.azure.com/"
log_analytics_workspace_id       = "/subscriptions/xxxxx/resourceGroups/ai-devops-rg/providers/Microsoft.OperationalInsights/workspaces/ai-devops-logs"
configure_kubectl                = "az aks get-credentials --resource-group ai-devops-rg --name ai-devops-aks"
```

## Cost Estimation

Approximate monthly costs (East US region):

| Resource | Configuration | Monthly Cost |
|----------|--------------|--------------|
| AKS Control Plane | Free tier | $0 |
| System Node Pool (3x D4s_v3) | 4 vCPU, 16 GB RAM each | ~$350 |
| AI Workload Pool (3x D8s_v3) | 8 vCPU, 32 GB RAM each | ~$700 |
| Application Insights | 5 GB/month | ~$12 |
| Log Analytics | 5 GB/month | ~$12 |
| VNet & Networking | Data transfer | ~$25 |
| **Total** | | **~$1,099/month** |

Note: Costs vary based on actual usage and region. Enable auto-scaling to optimize costs.

## Security Best Practices

1. **Network Isolation**: Private AKS cluster with VNet integration
2. **Managed Identity**: Use Azure AD managed identities for service access
3. **RBAC**: Enable Kubernetes RBAC and Azure AD integration
4. **Secrets Management**: Use Azure Key Vault for sensitive data
5. **Network Policies**: Implement Kubernetes network policies
6. **Pod Security**: Use Azure Policy for Kubernetes

## Monitoring and Observability

### Application Insights Dashboards

Access dashboards in Azure Portal:
1. Navigate to Application Insights resource
2. View pre-built dashboards:
   - Overview
   - Performance
   - Failures
   - Live Metrics

### Kusto Query Language (KQL) Examples

Query Application Insights with KQL:

```kusto
// Average inference latency
traces
| where name == "ai_inference"
| extend duration = todouble(customDimensions.duration_ms)
| summarize avg(duration) by bin(timestamp, 5m)
| render timechart

// Error rate analysis
traces
| where severityLevel >= 3
| summarize ErrorCount = count() by bin(timestamp, 1h), operation_Name
| render barchart

// Token usage by model
traces
| extend tokens = toint(customDimensions["tokens.used"])
| extend model = tostring(customDimensions["ai.model.name"])
| summarize TotalTokens = sum(tokens) by model, bin(timestamp, 1h)
| render columnchart

// Cost tracking
traces
| extend cost = todouble(customDimensions["ai.cost"])
| summarize TotalCost = sum(cost) by bin(timestamp, 1d)
| project timestamp, TotalCost, CumulativeCost = row_cumsum(TotalCost)
| render timechart
```

### Container Insights

View cluster metrics:
1. Navigate to AKS cluster in Azure Portal
2. Select **Monitoring → Insights**
3. View:
   - Cluster health
   - Node performance
   - Container logs
   - Workload metrics

### Azure Monitor Alerts

Create alerts for critical metrics:

```bash
# High latency alert
az monitor metrics alert create \
  --name "ai-high-latency" \
  --resource-group ai-devops-rg \
  --scopes /subscriptions/.../resourceGroups/ai-devops-rg/providers/microsoft.insights/components/ai-devops-insights \
  --condition "avg requests/duration > 1000" \
  --window-size 5m \
  --evaluation-frequency 1m

# High error rate alert
az monitor metrics alert create \
  --name "ai-high-error-rate" \
  --resource-group ai-devops-rg \
  --scopes /subscriptions/.../resourceGroups/ai-devops-rg/providers/microsoft.insights/components/ai-devops-insights \
  --condition "count requests/failed > 10" \
  --window-size 5m
```

## Troubleshooting

### Cluster not accessible

```bash
# Get AKS credentials
az aks get-credentials \
  --resource-group ai-devops-rg \
  --name ai-devops-aks \
  --overwrite-existing

# Verify cluster connectivity
kubectl get nodes
kubectl cluster-info
```

### Nodes not ready

```bash
# Check node status
kubectl get nodes
kubectl describe node <node-name>

# Check pod status
kubectl get pods -A
kubectl describe pod <pod-name> -n <namespace>

# View Container Insights
az aks show \
  --resource-group ai-devops-rg \
  --name ai-devops-aks \
  --query "addonProfiles.omsagent"
```

### Monitoring not working

```bash
# Verify Application Insights configuration
az monitor app-insights component show \
  --app ai-devops-insights \
  --resource-group ai-devops-rg

# Check Log Analytics workspace
az monitor log-analytics workspace show \
  --resource-group ai-devops-rg \
  --workspace-name ai-devops-logs
```

### High costs

- Review resource utilization in Container Insights
- Enable cluster auto-scaler
- Use spot instances for non-critical workloads
- Set budget alerts in Azure Cost Management
- Optimize Application Insights sampling rate

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all resources including data and logs. Ensure you have backups if needed.

## Advanced Configuration

### Enable Azure AD Integration

```bash
# Enable Azure AD RBAC
az aks update \
  --resource-group ai-devops-rg \
  --name ai-devops-aks \
  --enable-aad \
  --enable-azure-rbac
```

### Configure Auto-scaler

```bash
# Update cluster auto-scaler settings
az aks update \
  --resource-group ai-devops-rg \
  --name ai-devops-aks \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 20
```

### Enable Azure Policy

```bash
# Add Azure Policy add-on
az aks enable-addons \
  --resource-group ai-devops-rg \
  --name ai-devops-aks \
  --addons azure-policy
```

### Configure Azure Key Vault

```bash
# Create Key Vault
az keyvault create \
  --name ai-devops-kv \
  --resource-group ai-devops-rg \
  --location eastus

# Enable Key Vault integration
az aks enable-addons \
  --resource-group ai-devops-rg \
  --name ai-devops-aks \
  --addons azure-keyvault-secrets-provider
```

## Integration with Azure Services

### Azure Container Registry (ACR)

```bash
# Create ACR
az acr create \
  --resource-group ai-devops-rg \
  --name aidevopsacr \
  --sku Standard

# Integrate with AKS
az aks update \
  --resource-group ai-devops-rg \
  --name ai-devops-aks \
  --attach-acr aidevopsacr
```

### Azure OpenAI Service

```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
  --name ai-devops-openai \
  --resource-group ai-devops-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# Get endpoint and keys
az cognitiveservices account show \
  --name ai-devops-openai \
  --resource-group ai-devops-rg \
  --query "properties.endpoint"
```

### Azure Service Bus

```bash
# Create Service Bus namespace
az servicebus namespace create \
  --resource-group ai-devops-rg \
  --name ai-devops-bus \
  --location eastus \
  --sku Standard
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Deploy to AKS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - uses: azure/aks-set-context@v3
        with:
          resource-group: ai-devops-rg
          cluster-name: ai-devops-aks
      
      - run: |
          kubectl apply -f kubernetes/
```

### Azure DevOps

```yaml
trigger:
  - main

pool:
  vmImage: ubuntu-latest

steps:
  - task: AzureCLI@2
    inputs:
      azureSubscription: 'Azure Subscription'
      scriptType: 'bash'
      scriptLocation: 'inlineScript'
      inlineScript: |
        az aks get-credentials -g ai-devops-rg -n ai-devops-aks
        kubectl apply -f kubernetes/
```

## Scaling Strategies

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Vertical Pod Autoscaler (VPA)

```bash
# Install VPA
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.13.0/vpa-v0.13.0.yaml

# Create VPA resource
kubectl apply -f - <<EOF
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: ai-service-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-service
  updatePolicy:
    updateMode: "Auto"
EOF
```

## Resources

- [Azure Kubernetes Service Documentation](https://learn.microsoft.com/azure/aks/)
- [Application Insights Documentation](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Azure Monitor Documentation](https://learn.microsoft.com/azure/azure-monitor/)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [AKS Best Practices](https://learn.microsoft.com/azure/aks/best-practices)
- [Kusto Query Language](https://learn.microsoft.com/azure/data-explorer/kusto/query/)

## Support

For issues or questions:
1. Check [Azure AKS FAQ](https://learn.microsoft.com/azure/aks/faq)
2. Check [Application Insights FAQ](https://learn.microsoft.com/azure/azure-monitor/faq)
3. Open an issue in this repository
4. Consult Azure Support
