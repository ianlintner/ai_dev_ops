"""
Azure AI Foundry monitoring example with Application Insights.

This example demonstrates how to instrument AI workloads with
Azure Monitor and Application Insights.
"""

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode
import time
import random
import os

# Configure Azure Monitor
# Set APPLICATIONINSIGHTS_CONNECTION_STRING environment variable
connection_string = os.getenv(
    'APPLICATIONINSIGHTS_CONNECTION_STRING',
    'InstrumentationKey=00000000-0000-0000-0000-000000000000'
)

configure_azure_monitor(connection_string=connection_string)

# Get tracer and meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Create custom metrics
inference_counter = meter.create_counter(
    name="ai.azure.inference.requests",
    description="AI inference requests in Azure",
    unit="1"
)

inference_duration = meter.create_histogram(
    name="ai.azure.inference.duration",
    description="AI inference duration",
    unit="ms"
)


class AzureAIAgent:
    """AI Agent with Azure Monitor instrumentation."""
    
    def __init__(self, agent_id, model_name="gpt-4"):
        self.agent_id = agent_id
        self.model_name = model_name
    
    def process_request(self, user_input, user_id=None):
        """Process user request with Azure Monitor tracking."""
        with tracer.start_as_current_span("process_request") as span:
            # Set custom properties for Azure
            span.set_attribute("ai.agent.id", self.agent_id)
            span.set_attribute("ai.model.name", self.model_name)
            span.set_attribute("user.id", user_id or "anonymous")
            span.set_attribute("cloud.provider", "azure")
            span.set_attribute("cloud.region", "eastus")
            
            start_time = time.time()
            
            try:
                # Simulate AI processing
                with tracer.start_as_current_span("ai_inference") as inf_span:
                    inf_span.set_attribute("input.length", len(user_input))
                    
                    # Simulate inference
                    time.sleep(random.uniform(0.1, 0.5))
                    
                    tokens_used = random.randint(50, 200)
                    inf_span.set_attribute("tokens.used", tokens_used)
                    inf_span.set_attribute("model.version", "1.0.0")
                    
                    response = f"Processed: {user_input}"
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Record custom metrics
                inference_counter.add(1, {
                    "model": self.model_name,
                    "status": "success",
                    "cloud": "azure"
                })
                
                inference_duration.record(duration_ms, {
                    "model": self.model_name
                })
                
                # Add custom event
                span.add_event("Request processed successfully", {
                    "duration_ms": duration_ms,
                    "tokens": tokens_used
                })
                
                span.set_status(Status(StatusCode.OK))
                return response
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                
                inference_counter.add(1, {
                    "model": self.model_name,
                    "status": "error",
                    "cloud": "azure"
                })
                
                raise
    
    def batch_process(self, inputs):
        """Process multiple inputs with batch tracking."""
        with tracer.start_as_current_span("batch_process") as span:
            span.set_attribute("batch.size", len(inputs))
            span.set_attribute("ai.agent.id", self.agent_id)
            
            results = []
            for i, input_data in enumerate(inputs):
                with tracer.start_as_current_span(f"process_item_{i}") as item_span:
                    item_span.set_attribute("batch.item.index", i)
                    result = self.process_request(input_data)
                    results.append(result)
            
            span.set_attribute("batch.completed", len(results))
            return results


def simulate_azure_workload():
    """Simulate AI workload with Azure Monitor."""
    agent = AzureAIAgent(agent_id="azure-agent-001", model_name="gpt-4")
    
    print("Azure Monitor AI Example")
    print("=" * 50)
    print(f"Connection String: {connection_string[:50]}...")
    print("\nProcessing requests...")
    
    # Single requests
    for i in range(5):
        try:
            input_text = f"Request {i+1}: Analyze this data"
            result = agent.process_request(input_text, user_id=f"user-{i}")
            print(f"✓ Completed: {result[:50]}...")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        time.sleep(0.5)
    
    # Batch processing
    print("\nProcessing batch...")
    batch_inputs = [
        "Batch item 1",
        "Batch item 2",
        "Batch item 3"
    ]
    
    try:
        results = agent.batch_process(batch_inputs)
        print(f"✓ Batch completed: {len(results)} items")
    except Exception as e:
        print(f"✗ Batch error: {e}")
    
    # Allow time for telemetry to be sent to Azure
    print("\nWaiting for telemetry export...")
    time.sleep(5)
    
    print("\n✓ Telemetry sent to Azure Monitor")
    print("View in Azure Portal: Application Insights > Transaction search")


if __name__ == "__main__":
    simulate_azure_workload()
