"""
Prometheus metrics for AI model monitoring.

This example demonstrates how to collect and expose Prometheus metrics
for AI inference monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server, Info
import time
import random

# Define AI-specific metrics

# Counter for total inference requests
inference_requests_total = Counter(
    'ai_inference_requests_total',
    'Total number of AI inference requests',
    ['model', 'environment', 'status']
)

# Histogram for inference latency
inference_latency_seconds = Histogram(
    'ai_inference_latency_seconds',
    'Time taken for AI inference in seconds',
    ['model', 'environment'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Counter for token usage
tokens_used_total = Counter(
    'ai_tokens_used_total',
    'Total number of tokens used',
    ['model', 'token_type']
)

# Gauge for active inference requests
active_inferences = Gauge(
    'ai_active_inferences',
    'Number of currently active inference requests',
    ['model']
)

# Histogram for token generation rate
token_generation_rate = Histogram(
    'ai_token_generation_rate_tokens_per_second',
    'Rate of token generation in tokens per second',
    ['model'],
    buckets=(10, 25, 50, 75, 100, 150, 200)
)

# Counter for errors
inference_errors_total = Counter(
    'ai_inference_errors_total',
    'Total number of inference errors',
    ['model', 'error_type']
)

# Gauge for model cost
inference_cost_dollars = Counter(
    'ai_inference_cost_dollars_total',
    'Total cost of inference in dollars',
    ['model']
)

# Info metric for model metadata
model_info = Info(
    'ai_model',
    'Information about the AI model'
)


class AIModelMonitor:
    """AI Model with Prometheus metrics instrumentation."""
    
    def __init__(self, model_name="gpt-4", environment="production"):
        self.model_name = model_name
        self.environment = environment
        
        # Set model info
        model_info.info({
            'model_name': model_name,
            'version': '1.0.0',
            'environment': environment,
            'provider': 'openai'
        })
    
    def run_inference(self, input_text):
        """Run inference with metrics collection."""
        # Increment active inferences
        active_inferences.labels(model=self.model_name).inc()
        
        try:
            # Measure inference latency
            with inference_latency_seconds.labels(
                model=self.model_name,
                environment=self.environment
            ).time():
                # Simulate inference
                start_time = time.time()
                time.sleep(random.uniform(0.1, 1.0))
                
                # Simulate token generation
                input_tokens = len(input_text.split())
                output_tokens = random.randint(50, 200)
                
                # Calculate token generation rate
                duration = time.time() - start_time
                rate = output_tokens / duration
                
                token_generation_rate.labels(
                    model=self.model_name
                ).observe(rate)
                
                # Record token usage
                tokens_used_total.labels(
                    model=self.model_name,
                    token_type='input'
                ).inc(input_tokens)
                
                tokens_used_total.labels(
                    model=self.model_name,
                    token_type='output'
                ).inc(output_tokens)
                
                # Calculate and record cost (example: $0.00002 per token)
                total_tokens = input_tokens + output_tokens
                cost = total_tokens * 0.00002
                inference_cost_dollars.labels(
                    model=self.model_name
                ).inc(cost)
                
                # Record successful request
                inference_requests_total.labels(
                    model=self.model_name,
                    environment=self.environment,
                    status='success'
                ).inc()
                
                return f"Generated response with {output_tokens} tokens"
        
        except Exception as e:
            # Record error
            inference_errors_total.labels(
                model=self.model_name,
                error_type=type(e).__name__
            ).inc()
            
            inference_requests_total.labels(
                model=self.model_name,
                environment=self.environment,
                status='error'
            ).inc()
            
            raise
        
        finally:
            # Decrement active inferences
            active_inferences.labels(model=self.model_name).dec()


def simulate_ai_workload():
    """Simulate AI workload to generate metrics."""
    models = [
        AIModelMonitor("gpt-4", "production"),
        AIModelMonitor("claude-2", "production")
    ]
    
    print("Simulating AI workload...")
    print("Metrics available at http://localhost:8000")
    
    # Run continuous inference simulation
    request_count = 0
    while True:
        try:
            request_count += 1
            model = random.choice(models)
            
            # Simulate different input sizes
            input_text = " ".join(["word"] * random.randint(10, 100))
            
            result = model.run_inference(input_text)
            
            if request_count % 10 == 0:
                print(f"Processed {request_count} requests...")
            
            # Occasionally simulate errors
            if random.random() < 0.05:
                try:
                    raise ValueError("Simulated error")
                except ValueError as e:
                    inference_errors_total.labels(
                        model=model.model_name,
                        error_type="ValueError"
                    ).inc()
            
            # Small delay between requests
            time.sleep(random.uniform(0.1, 0.5))
            
        except KeyboardInterrupt:
            print("\nStopping simulation...")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue


if __name__ == "__main__":
    print("Prometheus AI Metrics Example")
    print("=" * 50)
    
    # Start Prometheus metrics server
    print("Starting Prometheus metrics server on port 8000...")
    start_http_server(8000)
    
    # Run workload simulation
    simulate_ai_workload()
