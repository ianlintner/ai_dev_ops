"""
AWS CloudWatch and X-Ray integration for AI services.

This example demonstrates:
- CloudWatch Logs with structured logging
- CloudWatch Metrics for custom AI metrics
- X-Ray distributed tracing
- Integration with AWS services
"""

import os
import json
import time
import random
from datetime import datetime
import boto3
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import logging

# Patch AWS SDK and other libraries
patch_all()

# Configure X-Ray recorder
xray_recorder.configure(
    service='ai-inference-service',
    context_missing='LOG_ERROR',
    sampling=True
)

# Initialize AWS clients
cloudwatch = boto3.client('cloudwatch', region_name=os.getenv('AWS_REGION', 'us-west-2'))
logs_client = boto3.client('logs', region_name=os.getenv('AWS_REGION', 'us-west-2'))

# Configure structured logging for CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CloudWatchLogger:
    """Custom logger for CloudWatch Logs."""

    def __init__(self, log_group='/aws/ai-devops/inference', log_stream=None):
        self.log_group = log_group
        self.log_stream = log_stream or f"inference-{datetime.now().strftime('%Y%m%d')}"
        self.sequence_token = None
        self._ensure_log_group()
        self._ensure_log_stream()

    def _ensure_log_group(self):
        """Ensure log group exists."""
        try:
            logs_client.create_log_group(logGroupName=self.log_group)
        except logs_client.exceptions.ResourceAlreadyExistsException:
            pass

    def _ensure_log_stream(self):
        """Ensure log stream exists."""
        try:
            logs_client.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
        except logs_client.exceptions.ResourceAlreadyExistsException:
            # Get sequence token for existing stream
            response = logs_client.describe_log_streams(
                logGroupName=self.log_group,
                logStreamNamePrefix=self.log_stream,
                limit=1
            )
            if response['logStreams']:
                self.sequence_token = response['logStreams'][0].get('uploadSequenceToken')

    def log(self, message, level='INFO', **kwargs):
        """Send structured log to CloudWatch."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level,
            'message': message,
            **kwargs
        }

        # Add X-Ray trace ID if available
        segment = xray_recorder.current_segment()
        if segment:
            log_entry['trace_id'] = segment.trace_id

        log_events = [{
            'timestamp': int(time.time() * 1000),
            'message': json.dumps(log_entry)
        }]

        try:
            params = {
                'logGroupName': self.log_group,
                'logStreamName': self.log_stream,
                'logEvents': log_events
            }
            if self.sequence_token:
                params['sequenceToken'] = self.sequence_token

            response = logs_client.put_log_events(**params)
            self.sequence_token = response.get('nextSequenceToken')

        except Exception as e:
            print(f"Failed to send log to CloudWatch: {e}")


class CloudWatchMetrics:
    """Helper class for CloudWatch custom metrics."""

    def __init__(self, namespace='AIDevOps'):
        self.namespace = namespace

    def put_metric(self, metric_name, value, unit='None', dimensions=None):
        """Send custom metric to CloudWatch."""
        metric_data = {
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.utcnow()
        }

        if dimensions:
            metric_data['Dimensions'] = [
                {'Name': k, 'Value': v} for k, v in dimensions.items()
            ]

        try:
            cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
        except Exception as e:
            print(f"Failed to send metric to CloudWatch: {e}")


class AIInferenceService:
    """AI Inference Service with AWS observability."""

    def __init__(self):
        self.logger = CloudWatchLogger()
        self.metrics = CloudWatchMetrics()

    @xray_recorder.capture('preprocess_data')
    def preprocess_data(self, data):
        """Preprocess input data with X-Ray tracing."""
        subsegment = xray_recorder.current_subsegment()
        subsegment.put_annotation('data_size', len(data))
        subsegment.put_metadata('preprocessing_type', 'normalize')

        # Simulate preprocessing
        time.sleep(random.uniform(0.01, 0.05))
        processed = data.lower().strip()

        self.logger.log(
            'Preprocessing completed',
            operation='preprocess',
            data_size=len(data)
        )

        return processed

    @xray_recorder.capture('model_inference')
    def model_inference(self, input_data, model_name='gpt-4'):
        """Perform model inference with tracing and metrics."""
        subsegment = xray_recorder.current_subsegment()
        subsegment.put_annotation('model_name', model_name)
        subsegment.put_annotation('input_length', len(input_data))

        start_time = time.time()

        # Simulate model inference
        inference_time = random.uniform(0.1, 0.5)
        time.sleep(inference_time)

        result = f"Response to: {input_data}"
        tokens_used = len(result.split())
        latency_ms = inference_time * 1000

        # Add metadata to X-Ray
        subsegment.put_metadata('tokens_used', tokens_used)
        subsegment.put_metadata('latency_ms', latency_ms)

        # Send metrics to CloudWatch
        dimensions = {
            'ModelName': model_name,
            'Environment': os.getenv('ENVIRONMENT', 'dev')
        }

        self.metrics.put_metric(
            'InferenceLatency',
            latency_ms,
            unit='Milliseconds',
            dimensions=dimensions
        )

        self.metrics.put_metric(
            'TokensUsed',
            tokens_used,
            unit='Count',
            dimensions=dimensions
        )

        self.metrics.put_metric(
            'InferenceCount',
            1,
            unit='Count',
            dimensions=dimensions
        )

        # Cost tracking
        cost = tokens_used * 0.00002
        self.metrics.put_metric(
            'InferenceCost',
            cost,
            unit='None',
            dimensions=dimensions
        )

        self.logger.log(
            'Inference completed',
            operation='inference',
            model=model_name,
            latency_ms=latency_ms,
            tokens=tokens_used,
            cost=cost
        )

        return result, tokens_used

    @xray_recorder.capture('postprocess_result')
    def postprocess_result(self, result):
        """Postprocess inference result."""
        subsegment = xray_recorder.current_subsegment()
        subsegment.put_annotation('result_length', len(result))

        time.sleep(random.uniform(0.01, 0.03))
        processed = result.upper()

        return processed

    @xray_recorder.capture('inference_pipeline')
    def inference_pipeline(self, user_input, model_name='gpt-4'):
        """Complete AI inference pipeline with AWS observability."""
        segment = xray_recorder.current_segment()
        segment.put_annotation('pipeline_version', '1.0.0')
        segment.put_annotation('model_name', model_name)

        try:
            # Step 1: Preprocess
            processed_input = self.preprocess_data(user_input)

            # Step 2: Model inference
            inference_result, tokens = self.model_inference(processed_input, model_name)

            # Step 3: Postprocess
            final_result = self.postprocess_result(inference_result)

            # Track success
            self.metrics.put_metric(
                'PipelineSuccess',
                1,
                unit='Count',
                dimensions={'ModelName': model_name}
            )

            self.logger.log(
                'Pipeline completed successfully',
                operation='pipeline',
                model=model_name,
                tokens=tokens
            )

            return final_result

        except Exception as e:
            # Track errors
            segment.put_annotation('error', True)
            segment.put_metadata('error_message', str(e))

            self.metrics.put_metric(
                'PipelineError',
                1,
                unit='Count',
                dimensions={
                    'ModelName': model_name,
                    'ErrorType': type(e).__name__
                }
            )

            self.logger.log(
                'Pipeline failed',
                level='ERROR',
                operation='pipeline',
                model=model_name,
                error=str(e),
                error_type=type(e).__name__
            )

            raise


if __name__ == "__main__":
    print("AWS CloudWatch and X-Ray AI Inference Example")
    print("=" * 50)

    # Start X-Ray segment
    with xray_recorder.in_segment('ai-inference-example') as segment:
        segment.put_annotation('example_run', True)

        service = AIInferenceService()

        # Test cases
        test_cases = [
            ("What is the weather today?", "gpt-4"),
            ("Explain quantum computing", "gpt-4"),
            ("Write a Python function", "gpt-3.5-turbo"),
        ]

        for i, (user_input, model) in enumerate(test_cases, 1):
            print(f"\nRequest {i}: {user_input} (Model: {model})")
            try:
                result = service.inference_pipeline(user_input, model)
                print(f"Result: {result[:50]}...")
            except Exception as e:
                print(f"Error: {e}")

            time.sleep(0.5)

    print("\n" + "=" * 50)
    print("Logs and metrics sent to AWS CloudWatch")
    print("Traces sent to AWS X-Ray")
    print("\nView in AWS Console:")
    print("- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups")
    print("- CloudWatch Metrics: https://console.aws.amazon.com/cloudwatch/home#metricsV2:graph")
    print("- X-Ray Service Map: https://console.aws.amazon.com/xray/home#/service-map")
