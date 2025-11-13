# Kubernetes Deployments for AI Services

This directory contains Kubernetes manifests for deploying AI inference services with production-grade configurations.

## Structure

```
kubernetes/
├── base/                    # Base Kustomize resources
│   ├── deployment.yaml      # AI service deployment
│   ├── service.yaml         # Service definitions
│   ├── configmap.yaml       # Configuration
│   ├── serviceaccount.yaml  # Service account with IRSA/Workload Identity
│   ├── hpa.yaml            # Horizontal Pod Autoscaler
│   ├── ingress.yaml        # Ingress configuration
│   ├── pdb.yaml            # Pod Disruption Budget
│   ├── namespace.yaml       # Namespace definition
│   └── kustomization.yaml   # Kustomize configuration
└── overlays/               # Environment-specific overlays
    ├── dev/                # Development environment
    └── prod/               # Production environment
```

## Features

### Base Configuration
- **Deployment**: 3 replicas with security context and resource limits
- **Service**: ClusterIP service with HTTP and metrics ports
- **HPA**: Auto-scaling from 3 to 20 replicas based on CPU, memory, and custom metrics
- **PDB**: Ensures minimum 2 pods available during disruptions
- **Ingress**: NGINX ingress with TLS and rate limiting
- **Security**: Non-root user, read-only filesystem, dropped capabilities

### Environment Overlays
- **Development**: 1 replica, reduced resources
- **Production**: 5 replicas, increased resources

## Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- Kustomize (built into kubectl 1.14+)
- Optional: NGINX Ingress Controller, cert-manager

## Quick Start

### Deploy to Development

```bash
# Apply development configuration
kubectl apply -k kubernetes/overlays/dev/

# Verify deployment
kubectl get pods -n ai-services
kubectl get svc -n ai-services
```

### Deploy to Production

```bash
# Apply production configuration
kubectl apply -k kubernetes/overlays/prod/

# Verify deployment
kubectl get pods -n ai-services
kubectl get hpa -n ai-services
```

### View Logs

```bash
# Stream logs from all pods
kubectl logs -f -l app=ai-inference -n ai-services

# View specific pod
kubectl logs -f <pod-name> -n ai-services
```

### Access Metrics

```bash
# Port forward to metrics endpoint
kubectl port-forward -n ai-services svc/ai-inference-service 9090:9090

# Access metrics
curl http://localhost:9090/metrics
```

## Configuration

### Environment Variables

Edit `base/configmap.yaml` to configure:
- Observability settings (metrics, tracing, logging)
- AI model configurations
- Caching parameters
- Rate limiting

### Resource Limits

Adjust resources in overlay patches:
```yaml
# overlays/prod/resource-patch.yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "2000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"
```

### Scaling

Modify HPA configuration in `base/hpa.yaml`:
```yaml
minReplicas: 3
maxReplicas: 20
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Cloud Provider Setup

### AWS (EKS)

1. Annotate service account with IAM role:
```yaml
# base/serviceaccount.yaml
annotations:
  eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT_ID:role/ai-inference-service-role
```

2. Deploy:
```bash
kubectl apply -k kubernetes/overlays/prod/
```

### GCP (GKE)

1. Annotate service account with GCP service account:
```yaml
# base/serviceaccount.yaml
annotations:
  iam.gke.io/gcp-service-account: ai-inference@PROJECT_ID.iam.gserviceaccount.com
```

2. Create IAM policy binding:
```bash
gcloud iam service-accounts add-iam-policy-binding \
  ai-inference@PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:PROJECT_ID.svc.id.goog[ai-services/ai-inference]"
```

## Ingress Configuration

### Install NGINX Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx
```

### Install cert-manager for TLS

```bash
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

### Update Ingress Host

Edit `base/ingress.yaml` to set your domain:
```yaml
spec:
  tls:
  - hosts:
    - ai-inference.yourdomain.com
  rules:
  - host: ai-inference.yourdomain.com
```

## Monitoring

### Prometheus Integration

The service exposes Prometheus metrics on port 9090:
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "9090"
  prometheus.io/path: "/metrics"
```

### Create ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ai-inference
  namespace: ai-services
spec:
  selector:
    matchLabels:
      app: ai-inference
  endpoints:
  - port: metrics
    interval: 30s
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n ai-services

# Check events
kubectl get events -n ai-services --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n ai-services
```

### HPA Not Scaling

```bash
# Check HPA status
kubectl get hpa -n ai-services
kubectl describe hpa ai-inference-hpa -n ai-services

# Check metrics server
kubectl top nodes
kubectl top pods -n ai-services
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n ai-services

# Test service internally
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://ai-inference-service.ai-services.svc.cluster.local/health
```

## Best Practices

1. **Security**
   - Always run as non-root user
   - Use read-only root filesystem
   - Drop all capabilities
   - Define resource limits

2. **Reliability**
   - Set appropriate liveness and readiness probes
   - Configure PodDisruptionBudget
   - Use anti-affinity rules

3. **Observability**
   - Expose metrics endpoint
   - Use structured logging
   - Implement distributed tracing

4. **Scaling**
   - Configure HPA based on actual load
   - Set stabilization windows
   - Use multiple scaling metrics

5. **Configuration**
   - Use ConfigMaps for configuration
   - Use Secrets for sensitive data
   - Version your configurations

## Cleanup

```bash
# Delete development deployment
kubectl delete -k kubernetes/overlays/dev/

# Delete production deployment
kubectl delete -k kubernetes/overlays/prod/

# Delete namespace (removes all resources)
kubectl delete namespace ai-services
```

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
