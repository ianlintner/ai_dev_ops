# AWS Infrastructure for AI DevOps

This Terraform configuration deploys a complete AWS infrastructure for running AI workloads with comprehensive monitoring and observability.

## Architecture

The infrastructure includes:
- **VPC**: Multi-AZ VPC with public and private subnets
- **EKS Cluster**: Managed Kubernetes cluster for AI workloads
- **Node Groups**: Separate node groups for CPU and GPU workloads
- **IAM Roles**: Service accounts with IRSA (IAM Roles for Service Accounts)
- **CloudWatch**: Logs, metrics, alarms, and dashboards

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- kubectl
- helm (optional)

## Quick Start

### 1. Initialize Terraform

```bash
cd terraform/aws
terraform init
```

### 2. Review and Customize Variables

Create a `terraform.tfvars` file:

```hcl
aws_region      = "us-west-2"
environment     = "dev"
cluster_name    = "ai-devops-cluster"
cluster_version = "1.28"

node_groups = {
  ai_workload = {
    desired_size   = 3
    max_size       = 10
    min_size       = 2
    instance_types = ["m5.2xlarge"]
    capacity_type  = "ON_DEMAND"
    disk_size      = 100
  }
  gpu_workload = {
    desired_size   = 0
    max_size       = 5
    min_size       = 0
    instance_types = ["g4dn.xlarge"]
    capacity_type  = "SPOT"
    disk_size      = 200
  }
}
```

### 3. Plan the Deployment

```bash
terraform plan -out=tfplan
```

### 4. Apply the Configuration

```bash
terraform apply tfplan
```

This will take approximately 15-20 minutes to create all resources.

### 5. Configure kubectl

```bash
aws eks update-kubeconfig --region us-west-2 --name ai-devops-cluster
```

### 6. Verify Cluster Access

```bash
kubectl get nodes
kubectl get pods --all-namespaces
```

## Module Structure

```
aws/
├── main.tf           # Root module configuration
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── vpc/              # VPC module
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── eks/              # EKS cluster module
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── iam/              # IAM roles and policies
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
└── cloudwatch/       # CloudWatch monitoring
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

## Features

### VPC Configuration
- Multi-AZ deployment (3 availability zones)
- Public subnets for load balancers
- Private subnets for workloads
- NAT Gateways for outbound internet access
- Proper tagging for EKS integration

### EKS Cluster
- Managed control plane
- OIDC provider for IRSA
- Multiple node groups (CPU and GPU)
- EKS managed add-ons (VPC CNI, CoreDNS, kube-proxy)
- Control plane logging enabled

### Node Groups
- **AI Workload**: On-demand instances for production workloads
- **GPU Workload**: Spot instances for cost-effective GPU processing
- Automatic scaling configuration
- Taints and labels for workload separation

### IAM Configuration
- Service account roles with IRSA
- Least privilege access policies
- CloudWatch Logs access
- CloudWatch Metrics publishing
- AWS X-Ray tracing
- Secrets Manager access

### CloudWatch Monitoring
- Log groups for application and system logs
- Container Insights for cluster metrics
- Custom metric alarms:
  - High inference latency
  - High error rate
  - High token usage
- Pre-configured dashboard

## Outputs

After deployment, Terraform will output:

```
vpc_id                      = "vpc-xxxxx"
eks_cluster_endpoint        = "https://xxxxx.eks.amazonaws.com"
eks_oidc_provider_arn       = "arn:aws:iam::xxxxx:oidc-provider/..."
cloudwatch_log_group        = "/aws/ai-devops/ai-devops-cluster"
configure_kubectl           = "aws eks update-kubeconfig --region us-west-2 --name ai-devops-cluster"
```

## Cost Estimation

Approximate monthly costs (us-west-2):

| Resource | Configuration | Monthly Cost |
|----------|--------------|--------------|
| EKS Control Plane | 1 cluster | $73 |
| EC2 Instances (m5.2xlarge) | 3 on-demand | ~$900 |
| NAT Gateways | 3 gateways | ~$100 |
| Data Transfer | Varies | ~$50-200 |
| CloudWatch Logs | 5GB/month | ~$3 |
| **Total** | | **~$1,126-1,276/month** |

Note: GPU instances (g4dn.xlarge) add ~$0.526/hour (~$380/month) per instance.

## Security Best Practices

1. **Network Isolation**: Workloads run in private subnets
2. **IAM Roles**: Use IRSA instead of instance profiles
3. **Secrets Management**: Use AWS Secrets Manager for API keys
4. **Control Plane Logging**: All API calls are logged
5. **Pod Security**: Consider using Pod Security Standards

## Monitoring and Observability

### CloudWatch Dashboards

Access the dashboard:
```bash
# Get dashboard URL from AWS Console
aws cloudwatch list-dashboards
```

### Log Queries

Query application logs:
```bash
aws logs tail /aws/ai-devops/ai-devops-cluster/application --follow
```

Query for errors:
```bash
aws logs filter-log-events \
  --log-group-name /aws/ai-devops/ai-devops-cluster/application \
  --filter-pattern "ERROR"
```

### Metrics

View custom metrics:
```bash
aws cloudwatch list-metrics --namespace AIDevOps
```

## Troubleshooting

### Cluster not accessible
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name ai-devops-cluster

# Verify AWS credentials
aws sts get-caller-identity
```

### Nodes not joining cluster
```bash
# Check node group status
aws eks describe-nodegroup \
  --cluster-name ai-devops-cluster \
  --nodegroup-name ai-devops-cluster-ai_workload

# Check CloudWatch logs
aws logs tail /aws/eks/ai-devops-cluster/cluster --follow
```

### High costs
- Review CloudWatch metrics for resource utilization
- Consider using Spot instances for non-critical workloads
- Enable Cluster Autoscaler
- Set up budget alerts

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all resources including logs. Ensure you have backups if needed.

## Advanced Configuration

### Enable GPU Support

For GPU workloads, install the NVIDIA device plugin:

```bash
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/main/nvidia-device-plugin.yml
```

### Enable Cluster Autoscaler

Deploy the Cluster Autoscaler:

```bash
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm install cluster-autoscaler autoscaler/cluster-autoscaler \
  --set autoDiscovery.clusterName=ai-devops-cluster \
  --set awsRegion=us-west-2
```

### Enable AWS Load Balancer Controller

For Ingress support:

```bash
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=ai-devops-cluster
```

## References

- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [CloudWatch Container Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html)
