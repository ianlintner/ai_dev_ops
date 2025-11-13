# CI/CD Integration for AI DevOps

This document describes how to integrate AI observability into CI/CD pipelines.

## GitHub Actions

### Example Workflow for AI Model Testing

```yaml
name: AI Model CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  APPLICATIONINSIGHTS_CONNECTION_STRING: ${{ secrets.APPINSIGHTS_CONNECTION_STRING }}
  DD_API_KEY: ${{ secrets.DD_API_KEY }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests with observability
        run: |
          # Set up OpenTelemetry for test tracing
          export OTEL_SERVICE_NAME="ai-model-tests"
          export OTEL_EXPORTER_OTLP_ENDPOINT="http://collector:4317"
          
          # Run tests
          pytest tests/ --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
  
  performance-test:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run performance tests
        run: |
          python examples/prometheus/ai_metrics.py &
          PID=$!
          sleep 10
          
          # Collect metrics
          curl -s http://localhost:8000 > metrics.txt
          
          # Analyze metrics
          python -c "
          import sys
          with open('metrics.txt') as f:
              data = f.read()
              if 'ai_inference_latency_seconds' not in data:
                  print('ERROR: Metrics not found')
                  sys.exit(1)
              print('✓ Metrics collection verified')
          "
          
          kill $PID
  
  deploy-staging:
    runs-on: ubuntu-latest
    needs: [test, performance-test]
    if: github.ref == 'refs/heads/develop'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # Add your deployment commands here
      
      - name: Configure observability
        run: |
          # Update environment variables
          echo "OTEL_SERVICE_NAME=ai-service-staging" >> $GITHUB_ENV
          echo "DD_ENV=staging" >> $GITHUB_ENV
      
      - name: Run smoke tests
        run: |
          # Smoke test with observability
          python tests/smoke_test.py --env staging
      
      - name: Create deployment annotation
        run: |
          # Annotate Grafana with deployment
          curl -X POST https://grafana.example.com/api/annotations \
            -H "Authorization: Bearer ${{ secrets.GRAFANA_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "text": "Deployment to staging - ${{ github.sha }}",
              "tags": ["deployment", "staging"],
              "time": '$(date +%s)000'
            }'
  
  deploy-production:
    runs-on: ubuntu-latest
    needs: [test, performance-test]
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          echo "Deploying to production environment"
          # Add your deployment commands here
      
      - name: Configure observability
        run: |
          echo "OTEL_SERVICE_NAME=ai-service-prod" >> $GITHUB_ENV
          echo "DD_ENV=production" >> $GITHUB_ENV
      
      - name: Create deployment markers
        run: |
          # Datadog deployment marker
          curl -X POST "https://api.datadoghq.com/api/v1/events" \
            -H "DD-API-KEY: ${{ secrets.DD_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "title": "Production Deployment",
              "text": "Deployed commit ${{ github.sha }}",
              "tags": ["deployment:production", "service:ai-inference"],
              "alert_type": "info"
            }'
          
          # Azure Monitor custom event
          # Add your Azure Monitor API call here
      
      - name: Monitor deployment
        run: |
          # Wait and monitor metrics for anomalies
          sleep 300  # 5 minutes
          
          # Check error rate
          python scripts/check_deployment_health.py \
            --threshold 0.05 \
            --window 5m
```

## GitLab CI

### Example `.gitlab-ci.yml`

```yaml
stages:
  - test
  - build
  - deploy
  - monitor

variables:
  DD_SITE: datadoghq.com
  OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317

test:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt pytest
    - pytest tests/ --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
  coverage: '/TOTAL.*\s+(\d+%)$/'

performance-test:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - python tests/performance_test.py
  artifacts:
    reports:
      metrics: metrics.txt

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t ai-service:$CI_COMMIT_SHA .
    - docker tag ai-service:$CI_COMMIT_SHA ai-service:latest
    - docker push ai-service:$CI_COMMIT_SHA

deploy-staging:
  stage: deploy
  environment:
    name: staging
  script:
    - kubectl set image deployment/ai-service ai-service=ai-service:$CI_COMMIT_SHA
    - kubectl rollout status deployment/ai-service
  only:
    - develop

deploy-production:
  stage: deploy
  environment:
    name: production
  script:
    - kubectl set image deployment/ai-service ai-service=ai-service:$CI_COMMIT_SHA
    - kubectl rollout status deployment/ai-service
  only:
    - main
  when: manual

monitor-deployment:
  stage: monitor
  script:
    - |
      # Create deployment annotation
      curl -X POST $GRAFANA_URL/api/annotations \
        -H "Authorization: Bearer $GRAFANA_API_KEY" \
        -d @- <<EOF
      {
        "text": "Deployment $CI_COMMIT_SHA to $CI_ENVIRONMENT_NAME",
        "tags": ["deployment", "$CI_ENVIRONMENT_NAME"],
        "time": $(date +%s)000
      }
      EOF
    
    - python scripts/monitor_deployment.py --duration 600
  dependencies:
    - deploy-production
```

## Infrastructure as Code

### Terraform Example

```hcl
# monitoring.tf

# Application Insights
resource "azurerm_application_insights" "ai_monitoring" {
  name                = "ai-${var.environment}-insights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  
  tags = {
    environment = var.environment
    service     = "ai-inference"
    managed_by  = "terraform"
  }
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "ai_logs" {
  name                = "ai-${var.environment}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Metric Alert - High Latency
resource "azurerm_monitor_metric_alert" "high_latency" {
  name                = "ai-high-latency-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_application_insights.ai_monitoring.id]
  description         = "Alert when AI inference latency exceeds threshold"
  
  criteria {
    metric_namespace = "Microsoft.Insights/components"
    metric_name      = "requests/duration"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 1000  # 1 second
  }
  
  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

# Action Group
resource "azurerm_monitor_action_group" "main" {
  name                = "ai-alerts-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "ai-alerts"
  
  email_receiver {
    name          = "oncall"
    email_address = var.oncall_email
  }
  
  webhook_receiver {
    name        = "slack"
    service_uri = var.slack_webhook_url
  }
}

# Outputs
output "instrumentation_key" {
  value     = azurerm_application_insights.ai_monitoring.instrumentation_key
  sensitive = true
}

output "connection_string" {
  value     = azurerm_application_insights.ai_monitoring.connection_string
  sensitive = true
}
```

## Docker Integration

### Dockerfile with Observability

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install OpenTelemetry auto-instrumentation
RUN pip install opentelemetry-distro opentelemetry-exporter-otlp
RUN opentelemetry-bootstrap -a install

# Environment variables for observability
ENV OTEL_SERVICE_NAME=ai-inference-service
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_METRICS_EXPORTER=otlp
ENV OTEL_LOGS_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317

# Healthcheck with metrics exposure
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run with auto-instrumentation
CMD ["opentelemetry-instrument", "python", "app.py"]
```

## Kubernetes Deployment

### Deployment with Observability

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-inference-service
  labels:
    app: ai-inference
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-inference
  template:
    metadata:
      labels:
        app: ai-inference
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: ai-service
        image: ai-inference:latest
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 8000
          name: metrics
        env:
        - name: OTEL_SERVICE_NAME
          value: "ai-inference-service"
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://otel-collector:4317"
        - name: DD_AGENT_HOST
          valueFrom:
            fieldRef:
              fieldPath: status.hostIP
        - name: DD_ENV
          value: "production"
        - name: DD_VERSION
          value: "1.0.0"
        - name: APPLICATIONINSIGHTS_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: ai-secrets
              key: appinsights-connection-string
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ai-inference-service
  labels:
    app: ai-inference
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    name: http
  - port: 8000
    targetPort: 8000
    name: metrics
  selector:
    app: ai-inference
```

## Best Practices

1. **Automate Everything**: Make observability part of your CI/CD pipeline
2. **Test Observability**: Include tests that verify metrics and traces are being generated
3. **Version Control**: Store dashboard and alert configurations in Git
4. **Environment Parity**: Use same observability stack across all environments
5. **Deployment Markers**: Always annotate deployments in your monitoring systems
6. **Gradual Rollout**: Monitor metrics during canary deployments
7. **Automated Rollback**: Configure automatic rollback on metric anomalies

## Monitoring Deployment Success

### Health Check Script

```python
#!/usr/bin/env python3
"""
Check deployment health by monitoring key metrics.
"""

import sys
import time
import requests
from datetime import datetime, timedelta

def check_error_rate(prometheus_url, threshold=0.05, window="5m"):
    """Check if error rate is below threshold."""
    query = f'''
        sum(rate(ai_inference_requests_total{{status="error"}}[{window}])) 
        / 
        sum(rate(ai_inference_requests_total[{window}]))
    '''
    
    response = requests.get(
        f"{prometheus_url}/api/v1/query",
        params={"query": query}
    )
    
    result = response.json()
    if result["data"]["result"]:
        error_rate = float(result["data"]["result"][0]["value"][1])
        print(f"Error rate: {error_rate:.2%}")
        
        if error_rate > threshold:
            print(f"ERROR: Error rate {error_rate:.2%} exceeds threshold {threshold:.2%}")
            return False
    
    return True

def check_latency(prometheus_url, threshold=1.0, window="5m"):
    """Check if P95 latency is below threshold."""
    query = f'''
        histogram_quantile(0.95, 
            rate(ai_inference_latency_seconds_bucket[{window}])
        )
    '''
    
    response = requests.get(
        f"{prometheus_url}/api/v1/query",
        params={"query": query}
    )
    
    result = response.json()
    if result["data"]["result"]:
        latency = float(result["data"]["result"][0]["value"][1])
        print(f"P95 latency: {latency:.3f}s")
        
        if latency > threshold:
            print(f"ERROR: Latency {latency:.3f}s exceeds threshold {threshold}s")
            return False
    
    return True

if __name__ == "__main__":
    prometheus_url = "http://prometheus:9090"
    
    checks = [
        check_error_rate(prometheus_url),
        check_latency(prometheus_url)
    ]
    
    if all(checks):
        print("✓ Deployment health check passed")
        sys.exit(0)
    else:
        print("✗ Deployment health check failed")
        sys.exit(1)
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
