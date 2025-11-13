# AI DevOps - Production-Grade Observability & Infrastructure

A comprehensive repository providing production-ready infrastructure, monitoring, and observability solutions for AI/ML systems at scale.

## 📋 Overview

This repository provides complete infrastructure-as-code, deployment manifests, and observability integrations for:
- **Cloud Infrastructure**: Production-ready Terraform modules for AWS and GCP
- **Kubernetes Deployments**: Complete manifests and Helm charts for AI services
- **AI Model Observability**: Comprehensive monitoring and tracing for AI/ML models
- **Multi-Cloud Integration**: AWS CloudWatch, X-Ray, GCP Cloud Monitoring, Datadog
- **Advanced Patterns**: Caching, security, rate limiting, and PII detection
- **Platform Integrations**: Ready-to-deploy configurations for popular monitoring tools

## 🗂️ Repository Structure

```
ai_dev_ops/
├── terraform/          # Infrastructure as Code
│   ├── aws/            # AWS EKS, VPC, IAM, CloudWatch
│   └── gcp/            # GCP GKE, VPC, IAM, Cloud Monitoring
├── kubernetes/         # Kubernetes manifests
│   ├── base/           # Base Kustomize resources
│   └── overlays/       # Environment-specific configurations
├── helm/               # Helm charts
│   └── ai-inference-service/  # Production-ready AI service chart
├── examples/           # Code samples and integrations
│   ├── opentelemetry/  # OpenTelemetry instrumentation
│   ├── azure/          # Azure Monitor examples
│   ├── prometheus/     # Prometheus metrics
│   ├── aws/            # AWS CloudWatch & X-Ray integration
│   ├── gcp/            # GCP Cloud Monitoring & Trace
│   ├── datadog/        # Datadog APM full integration
│   ├── caching/        # Redis caching patterns
│   └── security/       # Security best practices
├── integrations/       # Platform configurations
│   ├── grafana/        # Grafana dashboards and alerts
│   ├── datadog/        # Datadog integration configs
│   ├── azure-monitor/  # Azure Monitor configurations
│   ├── elastic-stack/  # Elasticsearch, Logstash, Kibana
│   ├── splunk/         # Splunk integration
│   └── newrelic/       # New Relic APM
├── data-formats/       # Schema definitions
│   ├── metrics/        # Metrics format specifications
│   ├── logs/           # Structured logging formats
│   └── traces/         # Distributed tracing formats
└── docs/               # Documentation and best practices
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker (for containerized examples)
- Access to a monitoring platform (Grafana, Azure Monitor, Datadog, etc.)

### Basic Setup

1. Clone the repository:
```bash
git clone https://github.com/ianlintner/ai_dev_ops.git
cd ai_dev_ops
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Deploy infrastructure (choose your cloud):
```bash
# AWS
cd terraform/aws
terraform init
terraform apply

# GCP
cd terraform/gcp
terraform init
terraform apply
```

4. Deploy AI services:
```bash
# Using Kubernetes manifests
kubectl apply -k kubernetes/overlays/prod/

# Or using Helm
helm install ai-inference helm/ai-inference-service \
  --namespace ai-services --create-namespace
```

5. Explore the examples:
```bash
cd examples/opentelemetry
python basic_instrumentation.py
```

## 📊 Code Examples

### OpenTelemetry Instrumentation
Monitor AI agents and workflows with distributed tracing:
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("ai_inference"):
    # Your AI model inference code here
    result = model.predict(data)
```

See [examples/opentelemetry](./examples/opentelemetry/) for complete examples.

### Redis Caching
Reduce costs with intelligent caching:
```python
from caching import CachedAIService

service = CachedAIService(cache_ttl=3600)
result = service.inference_with_cache(prompt, model='gpt-4')
print(f"Cache hit rate: {service.get_cache_stats()['hit_rate_percent']}%")
```

See [examples/caching](./examples/caching/) for complete examples.

### Security & Compliance
PII detection and rate limiting:
```python
from security import SecureAIService

service = SecureAIService()
result = service.secure_inference(api_key, user_input, model='gpt-4')
# Automatically detects and masks PII, enforces rate limits
```

See [examples/security](./examples/security/) for complete examples.

### Metrics Collection
Collect and export metrics in Prometheus format:
```python
from prometheus_client import Counter, Histogram

inference_counter = Counter('ai_inference_total', 'Total AI inferences')
inference_latency = Histogram('ai_inference_latency_seconds', 'Inference latency')
```

See [examples/prometheus](./examples/prometheus/) for complete examples.

## ☁️ Cloud Infrastructure

### AWS Infrastructure
Complete production-ready infrastructure:
- **EKS Cluster**: Managed Kubernetes with auto-scaling
- **VPC**: Multi-AZ networking with NAT gateways
- **IAM**: IRSA roles for workload identity
- **CloudWatch**: Metrics, logs, and dashboards
- **X-Ray**: Distributed tracing

Deploy with Terraform: [terraform/aws](./terraform/aws/)

### GCP Infrastructure
Full GCP deployment:
- **GKE Cluster**: Regional cluster with Workload Identity
- **VPC**: Private cluster with Cloud NAT
- **IAM**: Service accounts with least privilege
- **Cloud Monitoring**: Custom metrics and alerts
- **Cloud Trace**: Performance monitoring

Deploy with Terraform: [terraform/gcp](./terraform/gcp/)

### Kubernetes Deployments
Production-ready manifests:
- Base configurations with Kustomize
- Environment-specific overlays (dev, prod)
- HPA for auto-scaling
- PodDisruptionBudget for availability
- Security contexts and policies

See [kubernetes/](./kubernetes/) for manifests.

### Helm Charts
Simplified deployment:
- Configurable replica count
- Built-in autoscaling
- Ingress with TLS
- Resource management
- Observability enabled

Deploy with Helm: [helm/ai-inference-service](./helm/ai-inference-service/)

## 🔌 Observability Integrations

### Datadog
Full APM integration:
- Distributed tracing with ddtrace
- Custom metrics for AI workloads
- Log management with trace correlation
- Pre-built dashboards and monitors

See [examples/datadog](./examples/datadog/)

### AWS CloudWatch & X-Ray
Native AWS observability:
- CloudWatch Logs with structured logging
- Custom metrics for AI KPIs
- X-Ray distributed tracing
- Lambda function templates

See [examples/aws](./examples/aws/)

### GCP Cloud Monitoring & Trace
Native GCP observability:
- Cloud Monitoring custom metrics
- Cloud Trace integration
- Structured logging with Cloud Logging
- Performance dashboards

See [examples/gcp](./examples/gcp/)

### Grafana Dashboards
Pre-built dashboards:
- Model performance metrics
- Inference latency and throughput
- Error rates and anomaly detection
- Cost tracking

See [integrations/grafana](./integrations/grafana/)

### Azure Monitor
Azure AI Foundry observability:
- Application Insights integration
- Log Analytics workspace
- Custom metrics and alerts

See [integrations/azure-monitor](./integrations/azure-monitor/)

## 📋 Data Formats

### Metrics Format (Prometheus)
```
# HELP ai_inference_latency_seconds Time taken for AI inference
# TYPE ai_inference_latency_seconds histogram
ai_inference_latency_seconds{model="gpt-4",environment="production"} 0.542
```

### Structured Logs (JSON)
```json
{
  "timestamp": "2025-11-13T22:00:00Z",
  "level": "INFO",
  "message": "Inference completed",
  "model": "gpt-4",
  "latency_ms": 542,
  "tokens_used": 150
}
```

### Distributed Traces (OpenTelemetry)
```json
{
  "trace_id": "abcd1234efgh5678",
  "span_id": "ijkl9101",
  "operation": "model_inference",
  "parent_span_id": "mnop1121",
  "duration_ms": 542
}
```

See [data-formats](./data-formats/) for complete schema definitions.

## 📚 Best Practices

### Infrastructure
1. **Use Infrastructure as Code**: Terraform for reproducible deployments
2. **Multi-AZ Deployment**: Ensure high availability across availability zones
3. **Auto-scaling**: Configure HPA based on CPU, memory, and custom metrics
4. **Resource Limits**: Always define requests and limits for containers
5. **Security Contexts**: Run containers as non-root with minimal privileges

### Observability
1. **Instrument Early**: Add observability from the start of development
2. **Use Standard Formats**: Leverage OpenTelemetry and Prometheus standards
3. **Monitor Costs**: Track token usage and API costs religiously
4. **Detect Drift**: Monitor model performance degradation over time
5. **Automate Alerts**: Set up intelligent alerting for anomalies
6. **Trace Context**: Always correlate logs with traces using trace IDs

### Security
1. **API Key Management**: Never commit secrets, use secrets managers
2. **Rate Limiting**: Implement token bucket rate limiting
3. **PII Detection**: Automatically detect and mask sensitive data
4. **Input Validation**: Sanitize all user inputs
5. **Audit Logging**: Log all security events for compliance

### Performance
1. **Caching**: Use Redis for prompt and response caching
2. **Batching**: Batch requests when possible to reduce latency
3. **Connection Pooling**: Reuse connections to AI services
4. **Model Selection**: Choose appropriate models based on requirements

See [docs/best-practices.md](./docs/best-practices.md) for detailed guidelines.

## 🔧 Technologies & Tools

### Infrastructure
- **Terraform**: Infrastructure as Code for AWS and GCP
- **Kubernetes**: Container orchestration with EKS and GKE
- **Helm**: Package manager for Kubernetes applications
- **Kustomize**: Configuration management for Kubernetes

### Observability
- **OpenTelemetry**: Vendor-neutral distributed tracing and metrics
- **Prometheus**: Time-series metrics collection
- **Grafana**: Visualization and dashboards
- **Datadog**: Full-stack APM and monitoring
- **AWS CloudWatch & X-Ray**: Native AWS observability
- **GCP Cloud Monitoring & Trace**: Native GCP observability
- **Azure Monitor**: Cloud-native Azure monitoring

### Languages & Frameworks
- **Python 3.8+**: Primary language for examples
- **boto3**: AWS SDK
- **google-cloud**: GCP SDK
- **ddtrace**: Datadog tracing
- **redis-py**: Redis client

### Security & Performance
- **Redis**: Caching and session management
- **Rate Limiting**: Token bucket algorithm
- **PII Detection**: Pattern-based and ML-based detection

## 🤖 GitHub Copilot

This repository includes GitHub Copilot instructions in `.github/copilot-instructions.md` to help with:
- Code style and patterns
- AI-specific observability conventions
- Integration best practices
- Documentation standards

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run formatting
make format

# Run linting
make lint

# Run tests
make test

# Validate JSON schemas
make validate

# Run all checks
make all
```

### CI/CD

This repository uses GitHub Actions for:
- **Linting**: Code quality checks with flake8, pylint, black, and isort
- **Testing**: Validation across Python 3.8, 3.9, 3.10, and 3.11
- **Security**: Bandit and Safety scans
- **Documentation**: Markdown link checking

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details

## 🔗 Resources

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Azure AI Foundry Observability](https://learn.microsoft.com/azure/ai-studio/)
- [Grafana Dashboards](https://grafana.com/docs/)

## 📧 Contact

For questions or suggestions, please open an issue in this repository.
