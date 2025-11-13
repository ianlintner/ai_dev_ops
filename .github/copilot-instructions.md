# GitHub Copilot Instructions for AI DevOps Repository

## Repository Overview

This repository provides examples, integrations, and best practices for AI/ML observability and DevOps. It includes OpenTelemetry tracing, Prometheus metrics, and cloud monitoring integrations.

## Code Style Guidelines

### Python
- Use Python 3.8+ features
- Follow PEP 8 with 120 character line length
- Use type hints where appropriate
- Include docstrings for all public functions and classes
- Prefer explicit imports over wildcards

### Documentation
- Write clear, concise documentation with examples
- Include code snippets in markdown files
- Use proper markdown formatting
- Keep documentation up-to-date with code changes

## File Organization

```
ai_dev_ops/
├── examples/           # Runnable code examples
│   ├── opentelemetry/  # OpenTelemetry instrumentation
│   ├── azure/          # Azure Monitor examples
│   └── prometheus/     # Prometheus metrics
├── integrations/       # Platform configurations
│   ├── grafana/        # Grafana dashboards
│   ├── datadog/        # Datadog integration
│   └── azure-monitor/  # Azure Monitor config
├── data-formats/       # Schema definitions
│   ├── metrics/        # Metrics schemas
│   ├── logs/           # Log schemas
│   └── traces/         # Trace schemas
└── docs/               # Documentation
```

## Code Patterns

### OpenTelemetry Instrumentation

Always use context managers for spans:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("operation_name") as span:
    span.set_attribute("key", "value")
    # Your code here
```

### Metrics Collection

Use Prometheus client patterns:

```python
from prometheus_client import Counter, Histogram

counter = Counter('metric_name', 'Description', ['label1', 'label2'])
histogram = Histogram('metric_name_seconds', 'Description')

with histogram.time():
    # Timed operation
    counter.labels(label1='value1', label2='value2').inc()
```

### Error Handling

Always record exceptions in traces:

```python
try:
    result = operation()
except Exception as e:
    span.record_exception(e)
    span.set_status(Status(StatusCode.ERROR, str(e)))
    raise
```

## Testing

- All Python examples must be runnable
- Validate JSON schemas before committing
- Test examples with multiple Python versions
- Include error handling in examples

## Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Sanitize user input in examples
- Follow least privilege principle

## Documentation Requirements

When adding new examples:
1. Include a README.md in the example directory
2. Add docstrings to all functions
3. Provide usage examples
4. Explain key concepts
5. List prerequisites

When adding integrations:
1. Include setup instructions
2. Provide configuration examples
3. Document platform-specific requirements
4. Include troubleshooting section

## Commit Messages

Use conventional commit format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

## AI-Specific Considerations

### Token Usage Tracking
Always track token consumption in AI examples:

```python
span.set_attribute("ai.tokens.input", input_tokens)
span.set_attribute("ai.tokens.output", output_tokens)
span.set_attribute("ai.cost", calculate_cost(input_tokens, output_tokens))
```

### Model Identification
Always identify the model being used:

```python
span.set_attribute("ai.model.name", "gpt-4")
span.set_attribute("ai.model.version", "1.0.0")
span.set_attribute("ai.model.provider", "openai")
```

### Performance Metrics
Track key performance indicators:

```python
span.set_attribute("ai.inference.latency_ms", latency)
span.set_attribute("ai.tokens.per_second", tokens / duration)
```

## Common Patterns to Follow

### Configuration Management
Use environment variables with sensible defaults:

```python
import os

OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "ai-service")
```

### Logging
Use structured logging:

```python
import logging
import json

logger.info(json.dumps({
    "timestamp": "2025-11-13T22:00:00Z",
    "level": "INFO",
    "message": "Inference completed",
    "model": "gpt-4",
    "latency_ms": 542
}))
```

### Resource Management
Always clean up resources:

```python
from contextlib import contextmanager

@contextmanager
def model_session():
    session = create_session()
    try:
        yield session
    finally:
        session.close()
```

## Integration Specific Guidelines

### Grafana Dashboards
- Use template variables for flexibility
- Include alert configurations
- Document query patterns
- Provide screenshot examples

### Azure Monitor
- Use Terraform for IaC examples
- Include Kusto query examples
- Document cost optimization
- Provide security best practices

### Datadog
- Include tag conventions
- Document metric naming
- Provide alert examples
- Explain sampling strategies

## Dependencies

When adding dependencies:
1. Add to requirements.txt
2. Pin major versions for stability
3. Document why the dependency is needed
4. Consider security implications

## Review Checklist

Before submitting code:
- [ ] Code follows style guidelines
- [ ] Examples are tested and working
- [ ] Documentation is complete
- [ ] JSON schemas are valid
- [ ] No secrets in code
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Metrics are meaningful

## Questions?

Refer to:
- [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- [docs/best-practices.md](docs/best-practices.md) for observability patterns
- [docs/getting-started.md](docs/getting-started.md) for quick start guide
