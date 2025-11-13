"""
Google Cloud Monitoring and Cloud Trace integration for AI services.

This example demonstrates:
- Cloud Monitoring custom metrics
- Cloud Trace distributed tracing
- Cloud Logging structured logs
- Integration with Vertex AI
"""

import os
import time
import random
from datetime import datetime
from google.cloud import monitoring_v3
from google.cloud import logging as cloud_logging
from google.cloud import trace_v2
from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import AlwaysOnSampler


class GCPObservability:
    """Helper class for GCP observability."""

    def __init__(self, project_id):
        self.project_id = project_id
        self.project_name = f"projects/{project_id}"

        # Initialize clients
        self.metrics_client = monitoring_v3.MetricServiceClient()
        self.logging_client = cloud_logging.Client(project=project_id)
        self.logger = self.logging_client.logger('ai-inference')

        # Initialize tracer
        exporter = stackdriver_exporter.StackdriverExporter(
            project_id=project_id
        )
        self.tracer = Tracer(
            exporter=exporter,
            sampler=AlwaysOnSampler()
        )

    def log_structured(self, message, severity='INFO', **kwargs):
        """Send structured log to Cloud Logging."""
        log_entry = {
            'message': message,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            **kwargs
        }

        self.logger.log_struct(log_entry, severity=severity)

    def send_metric(self, metric_type, value, metric_kind='GAUGE', value_type='INT64',
                    labels=None):
        """Send custom metric to Cloud Monitoring."""
        series = monitoring_v3.TimeSeries()
        series.metric.type = f"custom.googleapis.com/ai/{metric_type}"
        series.resource.type = "k8s_container"
        series.resource.labels["project_id"] = self.project_id
        series.resource.labels["location"] = os.getenv('GCP_REGION', 'us-central1')
        series.resource.labels["cluster_name"] = os.getenv('CLUSTER_NAME', 'ai-cluster')
        series.resource.labels["namespace_name"] = "ai-services"
        series.resource.labels["pod_name"] = os.getenv('HOSTNAME', 'local')
        series.resource.labels["container_name"] = "ai-inference"

        if labels:
            for key, value in labels.items():
                series.metric.labels[key] = str(value)

        point = monitoring_v3.Point()
        point.value.int64_value = int(value) if value_type == 'INT64' else value
        point.interval.end_time.seconds = int(time.time())

        series.points = [point]

        try:
            self.metrics_client.create_time_series(
                name=self.project_name,
                time_series=[series]
            )
        except Exception as e:
            print(f"Failed to send metric: {e}")


class AIInferenceService:
    """AI Inference Service with GCP observability."""

    def __init__(self, project_id):
        self.observability = GCPObservability(project_id)

    def preprocess_data(self, data):
        """Preprocess input data with tracing."""
        with self.observability.tracer.span(name='preprocess_data') as span:
            span.add_attribute('data.size', len(data))
            span.add_attribute('preprocessing.type', 'normalize')

            # Simulate preprocessing
            time.sleep(random.uniform(0.01, 0.05))
            processed = data.lower().strip()

            self.observability.log_structured(
                'Preprocessing completed',
                operation='preprocess',
                data_size=len(data)
            )

            return processed

    def model_inference(self, input_data, model_name='gpt-4'):
        """Perform model inference with tracing and metrics."""
        with self.observability.tracer.span(name='model_inference') as span:
            span.add_attribute('model.name', model_name)
            span.add_attribute('input.length', len(input_data))

            start_time = time.time()

            # Simulate model inference
            inference_time = random.uniform(0.1, 0.5)
            time.sleep(inference_time)

            result = f"Response to: {input_data}"
            tokens_used = len(result.split())
            latency_ms = inference_time * 1000

            # Add span attributes
            span.add_attribute('tokens.used', tokens_used)
            span.add_attribute('latency.ms', latency_ms)

            # Send metrics
            labels = {'model_name': model_name}

            self.observability.send_metric(
                'inference_latency',
                int(latency_ms),
                labels=labels
            )

            self.observability.send_metric(
                'tokens_used',
                tokens_used,
                labels=labels
            )

            self.observability.send_metric(
                'inference_count',
                1,
                labels=labels
            )

            # Cost tracking
            cost_cents = int(tokens_used * 0.00002 * 100)
            self.observability.send_metric(
                'inference_cost_cents',
                cost_cents,
                labels=labels
            )

            self.observability.log_structured(
                'Inference completed',
                operation='inference',
                model=model_name,
                latency_ms=latency_ms,
                tokens=tokens_used
            )

            return result, tokens_used

    def postprocess_result(self, result):
        """Postprocess inference result."""
        with self.observability.tracer.span(name='postprocess_result') as span:
            span.add_attribute('result.length', len(result))

            time.sleep(random.uniform(0.01, 0.03))
            processed = result.upper()

            return processed

    def inference_pipeline(self, user_input, model_name='gpt-4'):
        """Complete AI inference pipeline with GCP observability."""
        with self.observability.tracer.span(name='inference_pipeline') as span:
            span.add_attribute('pipeline.version', '1.0.0')
            span.add_attribute('model.name', model_name)

            try:
                # Step 1: Preprocess
                processed_input = self.preprocess_data(user_input)

                # Step 2: Model inference
                inference_result, tokens = self.model_inference(
                    processed_input, model_name
                )

                # Step 3: Postprocess
                final_result = self.postprocess_result(inference_result)

                # Track success
                self.observability.send_metric(
                    'pipeline_success',
                    1,
                    labels={'model_name': model_name}
                )

                self.observability.log_structured(
                    'Pipeline completed successfully',
                    operation='pipeline',
                    model=model_name,
                    tokens=tokens
                )

                return final_result

            except Exception as e:
                # Track errors
                span.add_attribute('error', True)
                span.add_attribute('error.message', str(e))

                self.observability.send_metric(
                    'pipeline_error',
                    1,
                    labels={
                        'model_name': model_name,
                        'error_type': type(e).__name__
                    }
                )

                self.observability.log_structured(
                    'Pipeline failed',
                    severity='ERROR',
                    operation='pipeline',
                    model=model_name,
                    error=str(e)
                )

                raise


if __name__ == "__main__":
    print("GCP Cloud Monitoring and Trace AI Inference Example")
    print("=" * 50)

    project_id = os.getenv('GCP_PROJECT_ID', 'your-project-id')
    service = AIInferenceService(project_id)

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
    print("Logs, metrics, and traces sent to GCP")
    print("\nView in GCP Console:")
    print(f"- Cloud Monitoring: https://console.cloud.google.com/monitoring/metrics-explorer?project={project_id}")
    print(f"- Cloud Trace: https://console.cloud.google.com/traces/list?project={project_id}")
    print(f"- Cloud Logging: https://console.cloud.google.com/logs/query?project={project_id}")
