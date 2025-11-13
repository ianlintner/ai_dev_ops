"""
Datadog APM integration for AI inference services.

This example demonstrates how to instrument AI workloads with Datadog APM,
custom metrics, and distributed tracing.
"""

import os
import time
from ddtrace import tracer, patch_all
from datadog import initialize, statsd
import random

# Initialize Datadog
options = {
    'statsd_host': os.getenv('DD_AGENT_HOST', 'localhost'),
    'statsd_port': int(os.getenv('DD_STATSD_PORT', '8125')),
}
initialize(**options)

# Patch all supported libraries for automatic instrumentation
patch_all()

# Configure tracer
tracer.configure(
    hostname=os.getenv('DD_AGENT_HOST', 'localhost'),
    port=int(os.getenv('DD_TRACE_AGENT_PORT', '8126')),
    service='ai-inference-service',
    env=os.getenv('DD_ENV', 'dev'),
)


class AIInferenceService:
    """AI Inference Service with Datadog instrumentation."""

    def __init__(self):
        self.service_name = 'ai-inference'
        self.version = '1.0.0'

    @tracer.wrap(name='ai.preprocess', service='ai-inference')
    def preprocess_data(self, data):
        """Preprocess input data with tracing."""
        span = tracer.current_span()
        span.set_tag('data.size', len(data))
        span.set_tag('preprocessing.type', 'normalize')

        # Simulate preprocessing
        time.sleep(random.uniform(0.01, 0.05))
        processed = data.lower().strip()

        # Custom metric
        statsd.histogram(
            'ai.preprocessing.duration',
            time.time(),
            tags=['service:ai-inference', 'operation:preprocess']
        )

        return processed

    @tracer.wrap(name='ai.inference', service='ai-inference')
    def model_inference(self, input_data, model_name='gpt-4'):
        """Perform model inference with detailed tracing."""
        span = tracer.current_span()
        span.set_tag('model.name', model_name)
        span.set_tag('model.version', '1.0.0')
        span.set_tag('input.length', len(input_data))

        start_time = time.time()

        # Simulate model inference
        inference_time = random.uniform(0.1, 0.5)
        time.sleep(inference_time)

        result = f"Response to: {input_data}"
        tokens_used = len(result.split())

        # Set span attributes
        span.set_tag('inference.latency_ms', inference_time * 1000)
        span.set_tag('tokens.used', tokens_used)
        span.set_tag('inference.success', True)

        # Custom metrics
        statsd.increment(
            'ai.inference.count',
            tags=[f'model:{model_name}', 'status:success']
        )

        statsd.histogram(
            'ai.inference.latency',
            inference_time * 1000,
            tags=[f'model:{model_name}']
        )

        statsd.gauge(
            'ai.tokens.used',
            tokens_used,
            tags=[f'model:{model_name}', 'type:output']
        )

        # Cost tracking (example: $0.00002 per token)
        cost = tokens_used * 0.00002
        statsd.increment(
            'ai.cost.total',
            cost,
            tags=[f'model:{model_name}']
        )

        return result, tokens_used

    @tracer.wrap(name='ai.postprocess', service='ai-inference')
    def postprocess_result(self, result):
        """Postprocess inference result."""
        span = tracer.current_span()
        span.set_tag('result.length', len(result))

        # Simulate postprocessing
        time.sleep(random.uniform(0.01, 0.03))
        processed = result.upper()

        return processed

    @tracer.wrap(name='ai.pipeline', service='ai-inference', resource='inference')
    def inference_pipeline(self, user_input, model_name='gpt-4'):
        """Complete AI inference pipeline with Datadog tracking."""
        span = tracer.current_span()
        span.set_tag('pipeline.version', '1.0.0')
        span.set_tag('user.input', user_input[:50])
        span.set_tag('model.name', model_name)

        try:
            # Step 1: Preprocess
            processed_input = self.preprocess_data(user_input)

            # Step 2: Model inference
            inference_result, tokens = self.model_inference(processed_input, model_name)

            # Step 3: Postprocess
            final_result = self.postprocess_result(inference_result)

            span.set_tag('pipeline.success', True)
            span.set_tag('pipeline.tokens', tokens)

            # Pipeline success metric
            statsd.increment(
                'ai.pipeline.success',
                tags=[f'model:{model_name}']
            )

            return final_result

        except Exception as e:
            # Track errors
            span.set_tag('error', True)
            span.set_tag('error.msg', str(e))

            statsd.increment(
                'ai.pipeline.error',
                tags=[f'model:{model_name}', f'error.type:{type(e).__name__}']
            )

            raise


def monitor_service_health():
    """Send service health metrics to Datadog."""
    # Service health check
    statsd.service_check(
        'ai.inference.health',
        statsd.OK,
        tags=['service:ai-inference'],
        message='Service is healthy'
    )

    # Active requests gauge (example)
    active_requests = random.randint(0, 50)
    statsd.gauge(
        'ai.inference.active_requests',
        active_requests,
        tags=['service:ai-inference']
    )


if __name__ == "__main__":
    print("Datadog AI Inference Example")
    print("=" * 50)

    service = AIInferenceService()

    # Test inputs with different models
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

            # Send health metrics
            monitor_service_health()

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(0.5)

    print("\n" + "=" * 50)
    print("Metrics and traces sent to Datadog")
    print("View in Datadog UI:")
    print("- APM: https://app.datadoghq.com/apm/traces")
    print("- Metrics: https://app.datadoghq.com/metric/explorer")
    print("- Service Map: https://app.datadoghq.com/apm/map")
