# AWS CloudWatch and X-Ray Examples

This directory contains examples for monitoring AI workloads using AWS CloudWatch and X-Ray distributed tracing.

## Prerequisites

- AWS account with appropriate permissions
- AWS CLI configured with credentials
- Python 3.8+
- boto3 SDK
- aws-xray-sdk

## Setup

### 1. Install Dependencies

```bash
pip install boto3>=1.34.0 aws-xray-sdk>=2.12.0
```

Or install from the root requirements.txt:

```bash
cd /home/runner/work/ai_dev_ops/ai_dev_ops
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

```bash
# Option 1: Using AWS CLI
aws configure

# Option 2: Using environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-west-2"

# Option 3: Using IAM roles (recommended for EC2/ECS/Lambda)
# No configuration needed - uses instance profile
```

### 3. Set Environment Variables

```bash
export AWS_REGION="us-west-2"
export ENVIRONMENT="dev"
```

## Examples

### CloudWatch and X-Ray Integration

**File:** `cloudwatch_xray_example.py`

Complete AI inference pipeline with AWS observability:
- CloudWatch Logs with structured logging
- CloudWatch Metrics for custom AI metrics
- X-Ray distributed tracing
- Cost tracking and performance monitoring

**Run:**
```bash
python cloudwatch_xray_example.py
```

**Features:**
- Automatic trace correlation between logs and traces
- Custom metrics for inference latency, token usage, and costs
- Structured logging in JSON format
- Error tracking and alerting
- Sub-segment tracing for detailed performance analysis

### Lambda Function Example

**File:** `lambda_function.py`

Serverless AI inference with Lambda:
- CloudWatch integration for Lambda logs
- X-Ray tracing for Lambda functions
- Custom metrics publishing
- Event-driven architecture

**Deploy:**
```bash
# Package dependencies
mkdir package
pip install boto3 aws-xray-sdk -t package/
cd package
zip -r ../lambda_deployment.zip .
cd ..
zip -g lambda_deployment.zip lambda_function.py

# Create Lambda function (replace with your role ARN)
aws lambda create-function \
  --function-name ai-inference \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_deployment.zip \
  --timeout 30 \
  --memory-size 512 \
  --tracing-config Mode=Active
```

**Test:**
```bash
aws lambda invoke \
  --function-name ai-inference \
  --payload '{"input": "Test query", "model": "gpt-4"}' \
  response.json
cat response.json
```

## What Gets Monitored

### CloudWatch Logs
- Structured JSON logs with timestamps
- Log correlation with X-Ray trace IDs
- Operation-specific log groups
- Error and exception tracking

**Log Format:**
```json
{
  "timestamp": "2025-11-22T19:44:00Z",
  "level": "INFO",
  "message": "Inference completed",
  "operation": "inference",
  "model": "gpt-4",
  "latency_ms": 542.3,
  "tokens": 150,
  "cost": 0.003,
  "trace_id": "1-5f84c123-abc123def456789012345678"
}
```

### CloudWatch Metrics

Custom metrics published to the `AIDevOps` namespace:

| Metric Name | Unit | Description | Dimensions |
|-------------|------|-------------|------------|
| `InferenceLatency` | Milliseconds | Time taken for model inference | ModelName, Environment |
| `TokensUsed` | Count | Number of tokens consumed | ModelName, Environment |
| `InferenceCount` | Count | Number of inference requests | ModelName, Status, Environment |
| `InferenceCost` | None | Cost per inference in USD | ModelName, Environment |
| `PipelineSuccess` | Count | Successful pipeline completions | ModelName |
| `PipelineError` | Count | Failed pipeline executions | ModelName, ErrorType |

### X-Ray Traces

Distributed tracing with:
- **Service Map**: Visualize service dependencies
- **Trace Timeline**: See request flow and latency
- **Annotations**: Searchable metadata (model_name, user_id, etc.)
- **Metadata**: Additional context (tokens, costs, errors)

**Trace Hierarchy:**
```
ai-inference-example (segment)
├── inference_pipeline (subsegment)
│   ├── preprocess_data (subsegment)
│   ├── model_inference (subsegment)
│   └── postprocess_result (subsegment)
```

## Viewing Data in AWS Console

### CloudWatch Logs

1. Open [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/home)
2. Navigate to **Logs → Log groups**
3. Select `/aws/ai-devops/inference`
4. Use CloudWatch Logs Insights for queries

**Example Queries:**

```sql
-- Average inference latency
fields @timestamp, latency_ms
| filter operation = "inference"
| stats avg(latency_ms) as avg_latency by bin(5m)

-- Error analysis
fields @timestamp, message, error_type
| filter level = "ERROR"
| stats count() by error_type

-- Token usage by model
fields @timestamp, tokens, model
| filter operation = "inference"
| stats sum(tokens) as total_tokens by model

-- Cost tracking
fields @timestamp, cost, model
| filter operation = "inference"
| stats sum(cost) as total_cost by bin(1h)
```

### CloudWatch Metrics

1. Open [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/home#metricsV2:)
2. Select **Metrics → AIDevOps**
3. Choose metrics to visualize
4. Create dashboards and alarms

### X-Ray Service Map

1. Open [X-Ray Console](https://console.aws.amazon.com/xray/home#/service-map)
2. View service map showing:
   - Service nodes and connections
   - Latency and error rates
   - Request volume

### X-Ray Traces

1. Navigate to **X-Ray → Traces**
2. Filter by:
   - Time range
   - Response time
   - Status code
   - Annotations (model_name, user_id)
3. Click on traces to see detailed timeline

## CloudWatch Alarms

Create alarms for critical metrics:

```bash
# High latency alarm
aws cloudwatch put-metric-alarm \
  --alarm-name ai-high-latency \
  --alarm-description "Alert when inference latency exceeds 1 second" \
  --metric-name InferenceLatency \
  --namespace AIDevOps \
  --statistic Average \
  --period 300 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=ModelName,Value=gpt-4

# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name ai-high-error-rate \
  --alarm-description "Alert when error rate is high" \
  --metric-name PipelineError \
  --namespace AIDevOps \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1

# Token usage threshold
aws cloudwatch put-metric-alarm \
  --alarm-name ai-token-usage-high \
  --alarm-description "Alert when token usage exceeds threshold" \
  --metric-name TokensUsed \
  --namespace AIDevOps \
  --statistic Sum \
  --period 3600 \
  --threshold 100000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

## Infrastructure as Code

Deploy complete AWS infrastructure using Terraform:

```bash
cd ../../terraform/aws
terraform init
terraform plan
terraform apply
```

See [terraform/aws/README.md](../../terraform/aws/README.md) for details on:
- EKS cluster setup
- VPC configuration
- IAM roles and policies
- CloudWatch configuration
- Container Insights

## Best Practices

### 1. Logging
- Use structured logging (JSON format)
- Include trace IDs for correlation
- Add contextual information (model, user_id, etc.)
- Use appropriate log levels (INFO, ERROR, DEBUG)

### 2. Metrics
- Track key performance indicators (latency, throughput)
- Monitor costs and token usage
- Set up alarms for anomalies
- Use consistent dimensions for filtering

### 3. Tracing
- Use meaningful segment and subsegment names
- Add annotations for searchable attributes
- Include metadata for debugging context
- Enable sampling for high-volume applications

### 4. Cost Optimization
- Use sampling to reduce X-Ray costs
- Set appropriate CloudWatch Logs retention
- Archive old logs to S3
- Use metric filters instead of detailed logs

### 5. Security
- Never log sensitive data (API keys, PII)
- Use IAM roles instead of access keys
- Enable CloudWatch Logs encryption
- Restrict access with IAM policies

## Sampling Configuration

For high-volume applications, configure X-Ray sampling:

```python
from aws_xray_sdk.core import xray_recorder

# Sample 10% of requests
xray_recorder.configure(
    service='ai-inference-service',
    sampling=True,
    sampling_rules={
        "version": 2,
        "rules": [
            {
                "description": "Sample 10% of AI inference requests",
                "service_name": "*",
                "http_method": "*",
                "url_path": "*",
                "fixed_target": 1,
                "rate": 0.1
            }
        ],
        "default": {
            "fixed_target": 1,
            "rate": 0.1
        }
    }
)
```

## Troubleshooting

### Logs not appearing?
1. Verify AWS credentials are configured
2. Check IAM permissions for CloudWatch Logs
3. Ensure log group and stream exist
4. Check for network connectivity issues

### Metrics not showing?
1. Verify namespace and metric names
2. Check IAM permissions for CloudWatch PutMetricData
3. Allow time for metric propagation (up to 15 minutes)
4. Verify dimensions match exactly

### X-Ray traces not appearing?
1. Check X-Ray daemon is running (for EC2/ECS)
2. Verify IAM permissions for X-Ray
3. Ensure SDK is properly configured
4. Check sampling configuration

### High costs?
1. Review X-Ray sampling rates
2. Check CloudWatch Logs retention settings
3. Reduce metric cardinality
4. Use metric filters for common queries

## Cost Estimation

Approximate costs for AWS services (us-west-2 region):

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| CloudWatch Logs | 5 GB ingestion, 7-day retention | $2.50 |
| CloudWatch Metrics | 100 custom metrics | $30 |
| CloudWatch Alarms | 5 alarms | $0.50 |
| X-Ray | 1M traces @ 10% sampling | $5.00 |
| **Total** | | **~$38/month** |

Note: Costs scale with usage. Use sampling and retention policies to optimize.

## Integration with Other AWS Services

### ECS/Fargate
```python
# X-Ray daemon runs as sidecar container
# Set environment variable:
# AWS_XRAY_DAEMON_ADDRESS=xray-daemon:2000
```

### EKS
```yaml
# Deploy X-Ray daemon as DaemonSet
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: xray-daemon
spec:
  template:
    spec:
      containers:
      - name: xray-daemon
        image: amazon/aws-xray-daemon:latest
        ports:
        - containerPort: 2000
          protocol: UDP
```

### API Gateway
Enable X-Ray tracing in API Gateway and traces will automatically flow through.

### SQS/SNS
Messages automatically include X-Ray trace headers for end-to-end tracing.

## Resources

- [AWS X-Ray Developer Guide](https://docs.aws.amazon.com/xray/latest/devguide/)
- [CloudWatch Logs Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)
- [CloudWatch Metrics Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/)
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [X-Ray SDK for Python](https://docs.aws.amazon.com/xray-sdk-for-python/latest/reference/)
- [CloudWatch Logs Insights Query Syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html)

## Support

For issues or questions:
1. Check [AWS CloudWatch FAQs](https://aws.amazon.com/cloudwatch/faqs/)
2. Check [AWS X-Ray FAQs](https://aws.amazon.com/xray/faqs/)
3. Open an issue in this repository
4. Consult AWS Support
