# AI DevOps - Observability, Monitoring & Best Practices

A comprehensive repository of examples, code samples, integrations, and data formats for implementing AI observability and DevOps practices.

## 📋 Overview

This repository provides practical examples and reference implementations for:
- **AI Model Observability**: Monitoring AI/ML models in production
- **DevOps Integration**: CI/CD pipelines for AI systems
- **Telemetry & Tracing**: OpenTelemetry instrumentation for AI workflows
- **Metrics & Logging**: Structured data formats for AI operations
- **Platform Integrations**: Ready-to-use configurations for popular monitoring tools

## 🗂️ Repository Structure

```
ai_dev_ops/
├── examples/           # Code samples and implementation examples
│   ├── opentelemetry/  # OpenTelemetry instrumentation examples
│   ├── azure/          # Azure AI monitoring examples
│   └── prometheus/     # Prometheus metrics examples
├── integrations/       # Platform integration configurations
│   ├── grafana/        # Grafana dashboards and alerts
│   ├── datadog/        # Datadog integration examples
│   └── azure-monitor/  # Azure Monitor configurations
├── data-formats/       # Schema definitions and data format examples
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

3. Explore the examples:
```bash
cd examples/opentelemetry
python basic_instrumentation.py
```

## 📊 Examples

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

### Metrics Collection
Collect and export metrics in Prometheus format:
```python
from prometheus_client import Counter, Histogram

inference_counter = Counter('ai_inference_total', 'Total AI inferences')
inference_latency = Histogram('ai_inference_latency_seconds', 'Inference latency')
```

See [examples/prometheus](./examples/prometheus/) for complete examples.

## 🔌 Integrations

### Grafana Dashboards
Pre-built dashboards for visualizing AI metrics:
- Model performance metrics
- Inference latency and throughput
- Error rates and anomaly detection
- Cost tracking

See [integrations/grafana](./integrations/grafana/) for dashboard definitions.

### Azure Monitor
Configuration for Azure AI Foundry observability:
- Application Insights integration
- Log Analytics workspace setup
- Custom metrics and alerts

See [integrations/azure-monitor](./integrations/azure-monitor/) for configurations.

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

1. **Instrument Early**: Add observability from the start of development
2. **Use Standard Formats**: Leverage OpenTelemetry and Prometheus standards
3. **Monitor Costs**: Track token usage and API costs
4. **Detect Drift**: Monitor model performance degradation
5. **Automate Alerts**: Set up intelligent alerting for anomalies
6. **Document Everything**: Maintain clear documentation of metrics and traces

See [docs/best-practices.md](./docs/best-practices.md) for detailed guidelines.

## 🔧 Technologies Used

- **OpenTelemetry**: Distributed tracing and metrics
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Azure Monitor**: Cloud-native monitoring
- **Datadog**: Full-stack observability
- **Python**: Primary language for examples

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details

## 🔗 Resources

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Azure AI Foundry Observability](https://learn.microsoft.com/azure/ai-studio/)
- [Grafana Dashboards](https://grafana.com/docs/)

## 📧 Contact

For questions or suggestions, please open an issue in this repository.
