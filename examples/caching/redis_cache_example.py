"""
Redis-based caching for AI inference with observability.

This example demonstrates:
- Prompt caching to reduce API calls
- Response caching for common queries
- Cache hit/miss tracking
- TTL management
"""

import os
import time
import json
import hashlib
import redis
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

# Configure OpenTelemetry
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)


class CachedAIService:
    """AI service with intelligent caching."""

    def __init__(self, redis_host='localhost', redis_port=6379, cache_ttl=3600):
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        self.cache_ttl = cache_ttl
        self.cache_hits = 0
        self.cache_misses = 0

    def _generate_cache_key(self, prompt, model, parameters):
        """Generate deterministic cache key from inputs."""
        cache_input = {
            'prompt': prompt,
            'model': model,
            'parameters': parameters
        }
        cache_str = json.dumps(cache_input, sort_keys=True)
        return f"ai:cache:{hashlib.sha256(cache_str.encode()).hexdigest()}"

    @tracer.start_as_current_span("check_cache")
    def get_from_cache(self, cache_key):
        """Retrieve response from cache."""
        span = trace.get_current_span()
        span.set_attribute("cache.key", cache_key)

        try:
            cached_response = self.redis_client.get(cache_key)

            if cached_response:
                self.cache_hits += 1
                span.set_attribute("cache.hit", True)
                span.set_attribute("cache.hits", self.cache_hits)
                span.add_event("Cache hit")

                # Track cache hit metric
                self._track_cache_metric("hit")

                return json.loads(cached_response)
            else:
                self.cache_misses += 1
                span.set_attribute("cache.hit", False)
                span.set_attribute("cache.misses", self.cache_misses)
                span.add_event("Cache miss")

                # Track cache miss metric
                self._track_cache_metric("miss")

                return None

        except Exception as e:
            span.set_attribute("cache.error", str(e))
            span.record_exception(e)
            return None

    @tracer.start_as_current_span("save_to_cache")
    def save_to_cache(self, cache_key, response, ttl=None):
        """Save response to cache with TTL."""
        span = trace.get_current_span()
        span.set_attribute("cache.key", cache_key)
        span.set_attribute("cache.ttl", ttl or self.cache_ttl)

        try:
            self.redis_client.setex(
                cache_key,
                ttl or self.cache_ttl,
                json.dumps(response)
            )
            span.add_event("Response cached")
        except Exception as e:
            span.set_attribute("cache.error", str(e))
            span.record_exception(e)

    @tracer.start_as_current_span("ai_inference_with_cache")
    def inference_with_cache(self, prompt, model='gpt-4', parameters=None):
        """Perform AI inference with caching."""
        span = trace.get_current_span()
        span.set_attribute("model.name", model)
        span.set_attribute("prompt.length", len(prompt))

        parameters = parameters or {}

        # Generate cache key
        cache_key = self._generate_cache_key(prompt, model, parameters)
        span.set_attribute("cache.key", cache_key)

        # Check cache first
        cached_response = self.get_from_cache(cache_key)
        if cached_response:
            span.set_attribute("inference.cached", True)
            span.set_attribute("inference.latency_ms", 0)
            return cached_response

        # Cache miss - perform actual inference
        span.set_attribute("inference.cached", False)

        start_time = time.time()

        # Simulate AI inference
        time.sleep(0.3)  # Simulate API call
        response = {
            'result': f"AI response to: {prompt}",
            'model': model,
            'tokens_used': len(prompt.split()) + 20,
            'cached': False,
            'timestamp': time.time()
        }

        latency_ms = (time.time() - start_time) * 1000
        span.set_attribute("inference.latency_ms", latency_ms)
        span.set_attribute("tokens.used", response['tokens_used'])

        # Save to cache
        self.save_to_cache(cache_key, response)

        return response

    def _track_cache_metric(self, metric_type):
        """Track cache hit/miss metrics."""
        # This would send to your metrics system
        cache_hit_rate = (
            self.cache_hits / (self.cache_hits + self.cache_misses)
            if (self.cache_hits + self.cache_misses) > 0
            else 0
        )

        # Example: Send to Prometheus, CloudWatch, etc.
        # metrics.gauge('ai.cache.hit_rate', cache_hit_rate)
        # metrics.increment(f'ai.cache.{metric_type}')

    def get_cache_stats(self):
        """Get cache statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (
            (self.cache_hits / total_requests * 100)
            if total_requests > 0
            else 0
        )

        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2)
        }

    @tracer.start_as_current_span("invalidate_cache")
    def invalidate_cache(self, pattern="ai:cache:*"):
        """Invalidate cache entries matching pattern."""
        span = trace.get_current_span()
        span.set_attribute("cache.pattern", pattern)

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                span.set_attribute("cache.deleted_count", deleted)
                span.add_event(f"Deleted {deleted} cache entries")
                return deleted
            return 0
        except Exception as e:
            span.record_exception(e)
            return 0


# Example usage with semantic caching
class SemanticCachedAIService(CachedAIService):
    """AI service with semantic similarity caching."""

    def __init__(self, *args, similarity_threshold=0.85, **kwargs):
        super().__init__(*args, **kwargs)
        self.similarity_threshold = similarity_threshold

    def _compute_embedding(self, text):
        """Compute text embedding (simplified)."""
        # In production, use a real embedding model
        return text.lower().split()

    def _similarity(self, embedding1, embedding2):
        """Compute similarity between embeddings."""
        # Simplified Jaccard similarity
        set1, set2 = set(embedding1), set(embedding2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0

    @tracer.start_as_current_span("semantic_cache_lookup")
    def semantic_cache_lookup(self, prompt, model):
        """Look for semantically similar cached responses."""
        span = trace.get_current_span()

        # Get all cache keys
        cache_keys = self.redis_client.keys("ai:cache:*")

        prompt_embedding = self._compute_embedding(prompt)
        span.set_attribute("cache.keys_checked", len(cache_keys))

        best_match = None
        best_similarity = 0

        for key in cache_keys[:100]:  # Limit search
            try:
                cached_data = json.loads(self.redis_client.get(key))
                cached_prompt = cached_data.get('prompt', '')

                cached_embedding = self._compute_embedding(cached_prompt)
                similarity = self._similarity(prompt_embedding, cached_embedding)

                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = cached_data
            except:
                continue

        if best_match:
            span.set_attribute("semantic.match_found", True)
            span.set_attribute("semantic.similarity", best_similarity)
            return best_match

        span.set_attribute("semantic.match_found", False)
        return None


if __name__ == "__main__":
    print("AI Inference Caching Example")
    print("=" * 50)

    # Standard caching
    service = CachedAIService(cache_ttl=3600)

    test_prompts = [
        "What is machine learning?",
        "Explain neural networks",
        "What is machine learning?",  # Cache hit expected
        "Tell me about AI",
        "What is machine learning?",  # Cache hit expected
    ]

    print("\n=== Standard Caching ===")
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nRequest {i}: {prompt}")
        result = service.inference_with_cache(prompt)
        print(f"Cached: {result.get('cached', False)}")
        print(f"Result: {result['result'][:50]}...")

    stats = service.get_cache_stats()
    print(f"\n=== Cache Statistics ===")
    print(f"Cache Hits: {stats['cache_hits']}")
    print(f"Cache Misses: {stats['cache_misses']}")
    print(f"Hit Rate: {stats['hit_rate_percent']}%")

    # Semantic caching
    print("\n\n=== Semantic Caching ===")
    semantic_service = SemanticCachedAIService()

    similar_prompts = [
        "What is ML?",
        "Explain machine learning",  # Semantically similar
        "Define machine learning",   # Semantically similar
    ]

    for i, prompt in enumerate(similar_prompts, 1):
        print(f"\nRequest {i}: {prompt}")
        result = semantic_service.inference_with_cache(prompt)

    time.sleep(2)  # Allow spans to export
    print("\n" + "=" * 50)
    print("Caching example completed")
