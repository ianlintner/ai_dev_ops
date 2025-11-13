"""
Advanced OpenTelemetry instrumentation with custom metrics and context propagation.

This example demonstrates:
- Custom span attributes for AI-specific metrics
- Context propagation across service boundaries
- Error handling and exception tracking
- Custom events and annotations
"""

import random
import time

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode

# Configure resources
resource = Resource.create(
    {"service.name": "ai-agent-service", "service.version": "2.0.0", "deployment.environment": "production"}
)

# Configure tracing
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Configure metrics
metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

# Create custom metrics
inference_counter = meter.create_counter(
    name="ai.inference.requests", description="Total number of AI inference requests", unit="1"
)

inference_duration = meter.create_histogram(
    name="ai.inference.duration", description="AI inference duration in milliseconds", unit="ms"
)

token_usage = meter.create_counter(
    name="ai.tokens.used", description="Total tokens used in AI inference", unit="tokens"
)


class AIAgent:
    """AI Agent with comprehensive observability."""

    def __init__(self, agent_id, model_name="gpt-4"):
        self.agent_id = agent_id
        self.model_name = model_name

    def tool_call(self, tool_name, parameters):
        """Execute a tool call with tracing."""
        with tracer.start_as_current_span("tool_call") as span:
            span.set_attribute("tool.name", tool_name)
            span.set_attribute("tool.parameters", str(parameters))
            span.set_attribute("agent.id", self.agent_id)

            # Simulate tool execution
            execution_time = random.uniform(0.05, 0.2)
            time.sleep(execution_time)

            result = f"Tool {tool_name} executed with {parameters}"
            span.set_attribute("tool.result", result[:100])
            span.set_attribute("tool.success", True)

            return result

    def generate_response(self, prompt, context=None):
        """Generate AI response with detailed tracing."""
        with tracer.start_as_current_span("generate_response") as span:
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("model.name", self.model_name)
            span.set_attribute("prompt.length", len(prompt))

            if context:
                span.set_attribute("context.provided", True)
                span.set_attribute("context.length", len(context))

            start_time = time.time()

            try:
                # Simulate token generation
                tokens_generated = 0
                response_parts = []

                for i in range(random.randint(3, 8)):
                    chunk_tokens = random.randint(10, 30)
                    tokens_generated += chunk_tokens
                    response_parts.append(f"chunk_{i}")

                    span.add_event(
                        "Token chunk generated",
                        {"chunk.index": i, "chunk.tokens": chunk_tokens, "total.tokens": tokens_generated},
                    )

                    time.sleep(random.uniform(0.02, 0.05))

                duration_ms = (time.time() - start_time) * 1000

                # Record metrics
                inference_counter.add(1, {"model": self.model_name, "agent_id": self.agent_id})
                inference_duration.record(duration_ms, {"model": self.model_name})
                token_usage.add(tokens_generated, {"model": self.model_name, "type": "output"})

                # Set final attributes
                span.set_attribute("tokens.generated", tokens_generated)
                span.set_attribute("inference.duration_ms", duration_ms)
                span.set_attribute("tokens.per_second", tokens_generated / (duration_ms / 1000))

                response = " ".join(response_parts)
                span.set_status(Status(StatusCode.OK))

                return response

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

    def multi_step_workflow(self, task):
        """Execute a multi-step AI workflow with full observability."""
        with tracer.start_as_current_span("multi_step_workflow") as span:
            span.set_attribute("workflow.task", task)
            span.set_attribute("workflow.steps", 3)

            # Step 1: Analyze task
            with tracer.start_as_current_span("analyze_task") as analyze_span:
                analyze_span.set_attribute("task.complexity", "medium")
                time.sleep(random.uniform(0.05, 0.1))
                analysis = "Task analyzed"
                analyze_span.add_event("Analysis complete")

            # Step 2: Call tools
            with tracer.start_as_current_span("execute_tools") as tools_span:
                tool_result = self.tool_call("web_search", {"query": task})
                tools_span.set_attribute("tools.executed", 1)

            # Step 3: Generate final response
            with tracer.start_as_current_span("generate_final_response") as gen_span:
                response = self.generate_response(task, context=tool_result)
                gen_span.set_attribute("response.length", len(response))

            span.add_event("Workflow completed", {"total_steps": 3, "success": True})

            return response


def simulate_agent_conversation():
    """Simulate a conversation with an AI agent."""
    agent = AIAgent(agent_id="agent-001", model_name="gpt-4")

    with tracer.start_as_current_span("agent_conversation") as span:
        span.set_attribute("conversation.id", "conv-123")
        span.set_attribute("user.id", "user-456")

        tasks = ["Search for the latest AI news", "Analyze sentiment of customer feedback", "Generate a summary report"]

        results = []
        for i, task in enumerate(tasks, 1):
            span.add_event(f"Processing task {i}", {"task": task})
            result = agent.multi_step_workflow(task)
            results.append(result)

        span.set_attribute("conversation.tasks_completed", len(tasks))
        span.set_status(Status(StatusCode.OK))

        return results


if __name__ == "__main__":
    print("Advanced OpenTelemetry AI Agent Example")
    print("=" * 50)

    try:
        results = simulate_agent_conversation()
        print(f"\nCompleted {len(results)} tasks successfully")

        # Allow time for telemetry export
        time.sleep(3)

    except Exception as e:
        print(f"Error: {e}")

    print("\nTelemetry data (traces and metrics) exported to console above.")
