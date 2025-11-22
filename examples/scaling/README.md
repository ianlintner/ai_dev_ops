# AI-Powered Kubernetes Autoscaling

Intelligent scaling solutions that combine observability data with AI/LLM to make optimal scaling decisions for Kubernetes deployments.

## Overview

This directory contains examples and tools for using AI to manage Kubernetes scaling, including:

- **AI Scaling Decision Engine**: Uses LLM to analyze metrics and recommend scaling actions
- **HPA Manager**: Automatically updates Kubernetes HPA configurations based on AI recommendations
- **Schedule Generator**: Creates optimal scaling schedules from historical patterns
- **Test Datasets**: Realistic metrics for integration testing and validation

## Features

### 🤖 AI-Powered Decision Making
- Analyzes CPU, memory, request rates, error rates, and queue depth
- Provides confidence scores and detailed reasoning
- Supports both horizontal and vertical scaling recommendations
- Handles edge cases like memory constraints and over-provisioning

### 📊 Pattern Recognition
- Identifies daily peak hours and low-traffic periods
- Recognizes day-of-week variations (weekday vs weekend)
- Detects gradual trends vs sudden spikes
- Generates predictive scaling schedules

### ⚙️ HPA Management
- Automatically adjusts min/max replica counts
- Generates Kubernetes YAML configurations
- Dry-run mode for safe testing
- Integration with kubectl for cluster updates

### 💰 Cost Optimization
- Identifies over-provisioned resources
- Recommends scale-down opportunities
- Schedule-based scaling for predictable savings
- Cost impact estimation for decisions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Observability Data                        │
│  (Prometheus, CloudWatch, Azure Monitor, Datadog, etc.)      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  AI Scaling Engine                           │
│  • Analyzes current metrics                                  │
│  • Considers historical trends                               │
│  • Uses LLM for intelligent decisions                        │
│  • Provides confidence scores                                │
└────────────────────────┬────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
┌─────────────────────┐    ┌─────────────────────────┐
│   HPA Manager       │    │  Schedule Generator     │
│  • Updates min/max  │    │  • Analyzes patterns    │
│  • Applies configs  │    │  • Creates schedules    │
│  • Tracks changes   │    │  • Generates CronJobs   │
└─────────────────────┘    └─────────────────────────┘
            │                         │
            └────────────┬────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                         │
│  • HPA configurations                                        │
│  • Deployment replicas                                       │
│  • Resource limits                                           │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install -r ../../requirements.txt

# Optional: Set API key for AI-powered decisions
export ANTHROPIC_API_KEY="your-api-key-here"

# Optional: kubectl for cluster integration
kubectl version
```

### Run the Comprehensive Example

```bash
# From the examples/scaling directory
python comprehensive_example.py
```

This will demonstrate:
1. Real-time scaling decisions
2. HPA configuration management
3. Schedule generation from patterns
4. Cost optimization analysis
5. Vertical scaling recommendations

### Run Individual Examples

```bash
# AI Scaling Engine
python ai_scaling_engine.py

# HPA Manager
python k8s_hpa_manager.py

# Schedule Generator
python schedule_generator.py
```

## Usage Examples

### 1. Real-Time Scaling Decision

```python
from ai_scaling_engine import AIScalingEngine, ScalingMetrics

# Initialize engine
engine = AIScalingEngine()

# Create metrics from your observability platform
current_metrics = ScalingMetrics(
    cpu_utilization=88.0,
    memory_utilization=85.0,
    request_rate=620.0,
    response_time_ms=920.0,
    error_rate=11.2,
    active_connections=2380,
    queue_depth=158,
    current_pod_count=3
)

# Get AI recommendation
decision = engine.analyze_metrics(current_metrics)

print(f"Action: {decision.action}")
print(f"Recommended Pods: {decision.recommended_pod_count}")
print(f"Confidence: {decision.confidence:.2%}")
print(f"Reasoning: {decision.reasoning}")
```

### 2. Update HPA Configuration

```python
from k8s_hpa_manager import K8sHPAManager, HPAConfiguration

# Initialize manager (dry_run=False to apply changes)
manager = K8sHPAManager(dry_run=True)

# Define HPA configuration
hpa_config = HPAConfiguration(
    name="ai-inference-hpa",
    namespace="ai-services",
    min_replicas=3,
    max_replicas=20
)

# Update based on metrics
result = manager.update_hpa_from_metrics(hpa_config, current_metrics)

if result["applied"]:
    print(f"✓ HPA updated: {result['changes']}")
else:
    print(f"Dry-run: {result['note']}")
```

### 3. Generate Scaling Schedule

```python
from schedule_generator import ScheduleGenerator
from datetime import datetime, timedelta

# Initialize generator
generator = ScheduleGenerator()

# Prepare historical metrics (list of (timestamp, metrics) tuples)
metrics_history = []
for i in range(24):  # 24 hours of data
    timestamp = datetime.utcnow() - timedelta(hours=24-i)
    metrics = ScalingMetrics(...)  # Your metrics
    metrics_history.append((timestamp, metrics))

# Generate schedule
schedule = generator.generate_schedule(
    metrics_history,
    min_pods=3,
    max_pods=10
)

# Export as CronJobs
cron_jobs = schedule.to_cron_jobs()
for job in cron_jobs:
    print(f"{job['schedule']}: {job['kubectl_command']}")
```

## Test Datasets

The `test_data/metrics_dataset.json` file contains realistic scenarios:

### Available Scenarios

1. **normal_load**: Baseline operational metrics
2. **high_load_spike**: Sudden traffic spike requiring immediate scaling
3. **gradual_load_increase**: Progressive load increase for scheduled scaling
4. **memory_constrained**: High memory pressure requiring vertical scaling
5. **over_provisioned**: Low utilization indicating scale-down opportunity
6. **daily_peak_pattern**: 24-hour pattern with morning/evening peaks
7. **weekend_low_traffic**: Weekend traffic pattern for cost optimization
8. **flash_sale_event**: Planned high-traffic event requiring pre-scaling

### Using Test Data

```python
import json

# Load test scenarios
with open('test_data/metrics_dataset.json', 'r') as f:
    data = json.load(f)

# Use specific scenario
for scenario in data['scenarios']:
    if scenario['scenario'] == 'high_load_spike':
        metrics_data = scenario['metrics']
        # Use metrics for testing
```

## Integration with Observability Platforms

### Prometheus Integration

```python
from prometheus_client import Gauge
import time

# Query Prometheus for metrics
cpu_gauge = Gauge('cpu_utilization', 'CPU utilization')
memory_gauge = Gauge('memory_utilization', 'Memory utilization')

# Periodically analyze and scale
while True:
    current_metrics = ScalingMetrics(
        cpu_utilization=cpu_gauge._value.get(),
        memory_utilization=memory_gauge._value.get(),
        # ... other metrics
    )
    
    decision = engine.analyze_metrics(current_metrics)
    
    if decision.action != "maintain":
        manager.update_hpa_from_metrics(hpa_config, current_metrics)
    
    time.sleep(60)  # Check every minute
```

### CloudWatch Integration

```python
import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch')

# Get metrics from CloudWatch
response = cloudwatch.get_metric_statistics(
    Namespace='AWS/ECS',
    MetricName='CPUUtilization',
    Dimensions=[{'Name': 'ServiceName', 'Value': 'my-service'}],
    StartTime=datetime.utcnow() - timedelta(minutes=5),
    EndTime=datetime.utcnow(),
    Period=60,
    Statistics=['Average']
)

# Use with AI scaling engine
cpu_utilization = response['Datapoints'][0]['Average']
# ... create metrics and analyze
```

### Azure Monitor Integration

```python
from azure.monitor.query import MetricsQueryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = MetricsQueryClient(credential)

# Query metrics
response = client.query_resource(
    resource_uri="<resource-id>",
    metric_names=["Percentage CPU"],
    timespan=timedelta(minutes=5)
)

# Use with AI scaling engine
# ... process response and create metrics
```

## Configuration

### Environment Variables

```bash
# Required for AI-powered decisions
export ANTHROPIC_API_KEY="your-api-key"

# Optional: Configure Kubernetes context
export KUBECONFIG="/path/to/kubeconfig"

# Optional: Configure OpenTelemetry
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_SERVICE_NAME="ai-scaling-engine"
```

### HPA Configuration

Customize HPA behavior in your code:

```python
hpa_config = HPAConfiguration(
    name="my-service-hpa",
    namespace="production",
    min_replicas=2,              # Minimum pods
    max_replicas=50,             # Maximum pods
    target_cpu_utilization=70,   # Target CPU %
    target_memory_utilization=80 # Target Memory %
)
```

## Best Practices

### 1. Start with Dry-Run Mode
Always test with `dry_run=True` before applying changes to production:

```python
manager = K8sHPAManager(dry_run=True)
```

### 2. Monitor Confidence Scores
Only apply recommendations with high confidence:

```python
if decision.confidence > 0.75:
    # Apply the decision
    manager.update_hpa_from_metrics(hpa_config, current_metrics)
```

### 3. Set Appropriate Limits
Always define reasonable min/max pod counts:

```python
# Don't let HPA scale below minimum viable capacity
min_replicas = 3

# Don't exceed cluster capacity or budget
max_replicas = 20
```

### 4. Use Historical Data
Provide historical context for better decisions:

```python
decision = engine.analyze_metrics(
    current_metrics,
    historical_metrics=last_hour_metrics
)
```

### 5. Implement Gradual Changes
Don't make extreme changes too quickly:

```python
if decision.recommended_pod_count > current_count * 2:
    # Limit scale-up to 2x current capacity
    decision.recommended_pod_count = current_count * 2
```

### 6. Schedule-Based Scaling for Predictable Patterns
Use schedules for known patterns:

```python
# Generate weekly schedules
schedules = generator.generate_weekly_schedule(
    metrics_history,
    min_pods=3,
    max_pods=20
)

# Apply weekday schedule
weekday_schedule = schedules['weekday']
```

## OpenTelemetry Integration

All components include OpenTelemetry tracing:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

span_processor = BatchSpanProcessor(OTLPSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Traces are automatically created for:
# - analyze_metrics operations
# - HPA updates
# - Schedule generation
# - Pattern analysis
```

## Prometheus Metrics

The AI Scaling Engine exports Prometheus metrics:

- `ai_scaling_decisions_total{decision_type, confidence_level}`: Total scaling decisions
- `ai_scaling_analysis_latency_seconds`: Time to analyze metrics

Access metrics at `http://localhost:8000/metrics` (when Prometheus server is started).

## Troubleshooting

### AI Decisions Not Working

If AI-powered decisions aren't working:

1. Check API key is set: `echo $ANTHROPIC_API_KEY`
2. Verify network connectivity to Anthropic API
3. Check for error messages in output
4. Falls back to rule-based decisions automatically

### kubectl Commands Failing

If HPA updates fail:

1. Verify kubectl is installed: `kubectl version`
2. Check cluster access: `kubectl get nodes`
3. Verify namespace exists: `kubectl get namespaces`
4. Run in dry-run mode first: `dry_run=True`

### Test Data Not Found

If examples can't find test data:

```bash
# Ensure you're in the correct directory
cd examples/scaling

# Verify test data exists
ls -la test_data/metrics_dataset.json

# Run examples from the scaling directory
python comprehensive_example.py
```

## Cost Optimization Examples

### Scenario: Weekend Scale-Down

```python
# Weekend traffic is 60% lower
# Current: 8 pods @ $50/pod/month = $400/month
# Optimized: 3 pods @ $50/pod/month = $150/month
# Savings: $250/month = $3,000/year
```

### Scenario: Night-Time Scale-Down

```python
# Night hours (23:00-06:00): 7 hours/day = 213 hours/month
# Current: 5 pods = 1,065 pod-hours/month
# Optimized: 2 pods = 426 pod-hours/month
# Savings: 639 pod-hours @ $0.05/pod-hour = $32/month = $384/year
```

### Scenario: Pre-Peak Scaling

```python
# Pre-scale 30 minutes before peak instead of reactive scaling
# Reduces: Error rates from 15% to 2%
# Improves: Customer satisfaction and revenue retention
# Prevents: Service degradation and SLA violations
```

## Advanced Usage

### Custom Decision Logic

Extend the AI engine with custom rules:

```python
class CustomScalingEngine(AIScalingEngine):
    def _rule_based_decision(self, metrics):
        # Add custom logic
        if metrics.error_rate > 20:
            return ScalingDecision(
                action="scale_up_horizontal",
                recommended_pod_count=metrics.current_pod_count * 3,
                confidence=0.95,
                reasoning="Critical error rate threshold exceeded",
                urgency="critical"
            )
        
        return super()._rule_based_decision(metrics)
```

### Multi-Cluster Management

Manage HPAs across multiple clusters:

```python
clusters = ['prod-us-east', 'prod-eu-west', 'prod-ap-south']

for cluster in clusters:
    os.environ['KUBECONFIG'] = f'/path/to/{cluster}-config'
    manager = K8sHPAManager(dry_run=False)
    
    # Get cluster-specific metrics
    metrics = get_metrics_for_cluster(cluster)
    
    # Update HPA
    manager.update_hpa_from_metrics(hpa_config, metrics)
```

## Contributing

Contributions are welcome! Please ensure:

1. All examples are tested and working
2. Code follows repository style guidelines
3. Documentation is updated
4. Test datasets remain realistic

## Related Examples

- [OpenTelemetry Instrumentation](../opentelemetry/README.md)
- [Prometheus Metrics](../prometheus/README.md)
- [Multi-Agent Investigation](../multi-agent/README.md)
- [Azure Monitor Integration](../azure/README.md)

## License

MIT License - See [LICENSE](../../LICENSE) for details

## Resources

- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
