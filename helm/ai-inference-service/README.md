# Helm Chart for AI Inference Service

A production-ready Helm chart for deploying AI inference services with comprehensive observability.

## Features

- Configurable replica count and autoscaling
- Built-in Prometheus metrics
- OpenTelemetry tracing integration
- Security best practices (non-root, read-only filesystem)
- Ingress with TLS support
- PodDisruptionBudget for high availability
- Resource limits and requests
- Liveness and readiness probes

## Prerequisites

- Kubernetes 1.25+
- Helm 3.0+

## Installation

### Add the Chart Repository

```bash
# If publishing to a chart repository
helm repo add ai-devops https://charts.example.com
helm repo update
```

### Install from Local Directory

```bash
# Install with default values
helm install ai-inference ./helm/ai-inference-service

# Install with custom values
helm install ai-inference ./helm/ai-inference-service \
  --values custom-values.yaml

# Install in specific namespace
helm install ai-inference ./helm/ai-inference-service \
  --namespace ai-services \
  --create-namespace
```

## Configuration

### Basic Configuration

Create a `values.yaml` file:

```yaml
replicaCount: 5

image:
  repository: your-registry/ai-inference
  tag: "1.0.0"

resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"

ingress:
  enabled: true
  hosts:
    - host: ai-inference.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
```

### Production Configuration

```yaml
replicaCount: 10

autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 50
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

resources:
  requests:
    memory: "4Gi"
    cpu: "2000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"

affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
            - key: app.kubernetes.io/name
              operator: In
              values:
                - ai-inference-service
        topologyKey: kubernetes.io/hostname

pdb:
  enabled: true
  minAvailable: 3
```

### Observability Configuration

```yaml
config:
  observability:
    metrics:
      enabled: true
      port: 9090
    tracing:
      enabled: true
      sampleRate: 0.1  # Sample 10% of requests
    logging:
      level: info
      format: json

env:
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://otel-collector:4317"
  - name: OTEL_SERVICE_NAME
    value: "ai-inference-service"
```

## Configuration Parameters

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `3` |
| `image.repository` | Image repository | `ai-inference` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |

### Service Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `8000` |
| `service.metricsPort` | Metrics port | `9090` |

### Ingress Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.hosts` | Ingress hosts | `[]` |
| `ingress.tls` | TLS configuration | `[]` |

### Autoscaling Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable HPA | `true` |
| `autoscaling.minReplicas` | Minimum replicas | `3` |
| `autoscaling.maxReplicas` | Maximum replicas | `20` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU % | `70` |
| `autoscaling.targetMemoryUtilizationPercentage` | Target memory % | `80` |

### Resource Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.requests.memory` | Memory request | `2Gi` |
| `resources.requests.cpu` | CPU request | `1000m` |
| `resources.limits.memory` | Memory limit | `4Gi` |
| `resources.limits.cpu` | CPU limit | `2000m` |

## Examples

### Development Environment

```bash
helm install ai-inference ./helm/ai-inference-service \
  --set replicaCount=1 \
  --set resources.requests.memory=1Gi \
  --set resources.requests.cpu=500m \
  --set autoscaling.enabled=false \
  --set ingress.enabled=false
```

### Staging Environment

```bash
helm install ai-inference ./helm/ai-inference-service \
  --values values-staging.yaml \
  --namespace ai-staging \
  --create-namespace
```

### Production Environment

```bash
helm install ai-inference ./helm/ai-inference-service \
  --values values-production.yaml \
  --namespace ai-production \
  --create-namespace
```

## Upgrading

```bash
# Upgrade with new image tag
helm upgrade ai-inference ./helm/ai-inference-service \
  --set image.tag=1.1.0

# Upgrade with new values file
helm upgrade ai-inference ./helm/ai-inference-service \
  --values new-values.yaml

# Force recreation of pods
helm upgrade ai-inference ./helm/ai-inference-service \
  --recreate-pods
```

## Uninstalling

```bash
# Uninstall the release
helm uninstall ai-inference

# Uninstall and delete namespace
helm uninstall ai-inference --namespace ai-services
kubectl delete namespace ai-services
```

## Testing

```bash
# Test the chart
helm lint ./helm/ai-inference-service

# Dry run
helm install ai-inference ./helm/ai-inference-service --dry-run --debug

# Template rendering
helm template ai-inference ./helm/ai-inference-service
```

## Monitoring

### Access Metrics

```bash
# Port forward to metrics endpoint
kubectl port-forward svc/ai-inference-service 9090:9090

# Curl metrics
curl http://localhost:9090/metrics
```

### View Logs

```bash
# Get all pods
kubectl get pods -l app.kubernetes.io/name=ai-inference-service

# Follow logs
kubectl logs -f -l app.kubernetes.io/name=ai-inference-service
```

### Check Health

```bash
# Port forward to service
kubectl port-forward svc/ai-inference-service 8000:80

# Health check
curl http://localhost:8000/health

# Ready check
curl http://localhost:8000/ready
```

## Troubleshooting

### Chart Won't Install

```bash
# Check for errors
helm install ai-inference ./helm/ai-inference-service --dry-run --debug

# Validate chart
helm lint ./helm/ai-inference-service
```

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check resource constraints
kubectl top nodes
kubectl top pods
```

### HPA Not Working

```bash
# Check HPA status
kubectl get hpa
kubectl describe hpa ai-inference-service

# Ensure metrics-server is running
kubectl get deployment metrics-server -n kube-system
```

## Development

### Local Development

```bash
# Install chart from local directory
helm install ai-inference-dev ./helm/ai-inference-service \
  --values dev-values.yaml \
  --namespace dev

# Make changes and upgrade
helm upgrade ai-inference-dev ./helm/ai-inference-service
```

### Package Chart

```bash
# Package the chart
helm package ./helm/ai-inference-service

# Create chart repository index
helm repo index . --url https://charts.example.com
```

## Best Practices

1. **Always specify resource limits** to prevent resource exhaustion
2. **Enable autoscaling** for production workloads
3. **Configure PodDisruptionBudget** to maintain availability
4. **Use anti-affinity rules** to spread pods across nodes
5. **Enable ingress with TLS** for secure external access
6. **Configure proper health checks** for reliability
7. **Use structured logging** with JSON format
8. **Enable metrics** for observability

## References

- [Helm Documentation](https://helm.sh/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
