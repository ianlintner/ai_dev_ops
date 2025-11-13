"""
Basic OpenTelemetry instrumentation example for AI model inference.

This example demonstrates how to instrument an AI inference workflow
with OpenTelemetry tracing.
"""

import random
import time

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# Configure OpenTelemetry
resource = Resource.create({"service.name": "ai-inference-service"})
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(tracer_provider)

# Get a tracer
tracer = trace.get_tracer(__name__)


def preprocess_data(data):
    """Simulate data preprocessing with tracing."""
    with tracer.start_as_current_span("preprocess_data") as span:
        span.set_attribute("data.size", len(data))
        span.set_attribute("preprocessing.type", "normalize")

        # Simulate preprocessing work
        time.sleep(random.uniform(0.01, 0.05))
        processed = data.lower().strip()

        span.add_event("Preprocessing completed", {"processed.length": len(processed)})
        return processed


def model_inference(input_data):
    """Simulate AI model inference with tracing."""
    with tracer.start_as_current_span("model_inference") as span:
        span.set_attribute("model.name", "gpt-4")
        span.set_attribute("model.version", "1.0.0")
        span.set_attribute("input.length", len(input_data))

        # Simulate model inference
        inference_time = random.uniform(0.1, 0.5)
        time.sleep(inference_time)

        result = f"Response to: {input_data}"
        tokens_used = len(result.split())

        span.set_attribute("inference.latency_ms", inference_time * 1000)
        span.set_attribute("tokens.used", tokens_used)
        span.set_attribute("inference.success", True)

        span.add_event("Inference completed", {"tokens": tokens_used, "latency": inference_time})

        return result


def postprocess_result(result):
    """Simulate result postprocessing with tracing."""
    with tracer.start_as_current_span("postprocess_result") as span:
        span.set_attribute("result.length", len(result))

        # Simulate postprocessing
        time.sleep(random.uniform(0.01, 0.03))
        processed = result.upper()

        span.add_event("Postprocessing completed")
        return processed


def ai_inference_pipeline(user_input):
    """Complete AI inference pipeline with distributed tracing."""
    with tracer.start_as_current_span("ai_inference_pipeline") as span:
        span.set_attribute("pipeline.version", "1.0.0")
        span.set_attribute("user.input", user_input[:50])  # Truncate for privacy

        try:
            # Step 1: Preprocess
            processed_input = preprocess_data(user_input)

            # Step 2: Model inference
            inference_result = model_inference(processed_input)

            # Step 3: Postprocess
            final_result = postprocess_result(inference_result)

            span.set_attribute("pipeline.success", True)
            span.add_event("Pipeline completed successfully")

            return final_result

        except Exception as e:
            span.set_attribute("pipeline.success", False)
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise


if __name__ == "__main__":
    print("OpenTelemetry AI Inference Example")
    print("=" * 50)

    # Run multiple inference requests
    test_inputs = ["What is the weather today?", "Explain quantum computing", "Write a Python function"]

    for i, user_input in enumerate(test_inputs, 1):
        print(f"\nRequest {i}: {user_input}")
        try:
            result = ai_inference_pipeline(user_input)
            print(f"Result: {result[:50]}...")
        except Exception as e:
            print(f"Error: {e}")

    # Allow time for spans to be exported
    time.sleep(2)
    print("\nTracing data exported to console above.")
