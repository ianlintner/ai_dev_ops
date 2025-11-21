"""
AI-Powered Scaling Decision Engine

This module uses AI/LLM to analyze observability metrics and make intelligent
scaling decisions for Kubernetes deployments.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from opentelemetry import trace
from prometheus_client import Counter, Histogram

# Define metrics for the scaling engine itself
scaling_decisions_total = Counter(
    "ai_scaling_decisions_total",
    "Total number of AI scaling decisions made",
    ["decision_type", "confidence_level"],
)

scaling_analysis_latency = Histogram(
    "ai_scaling_analysis_latency_seconds",
    "Time taken to analyze metrics and make scaling decision",
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0),
)


tracer = trace.get_tracer(__name__)


class ScalingMetrics:
    """Container for current system metrics."""

    def __init__(
        self,
        cpu_utilization: float,
        memory_utilization: float,
        request_rate: float,
        response_time_ms: float,
        error_rate: float,
        active_connections: int,
        queue_depth: int,
        current_pod_count: int,
        timestamp: Optional[datetime] = None,
    ):
        self.cpu_utilization = cpu_utilization
        self.memory_utilization = memory_utilization
        self.request_rate = request_rate
        self.response_time_ms = response_time_ms
        self.error_rate = error_rate
        self.active_connections = active_connections
        self.queue_depth = queue_depth
        self.current_pod_count = current_pod_count
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "cpu_utilization_percent": self.cpu_utilization,
            "memory_utilization_percent": self.memory_utilization,
            "request_rate_per_second": self.request_rate,
            "response_time_ms": self.response_time_ms,
            "error_rate_percent": self.error_rate,
            "active_connections": self.active_connections,
            "queue_depth": self.queue_depth,
            "current_pod_count": self.current_pod_count,
            "timestamp": self.timestamp.isoformat(),
        }


class ScalingDecision:
    """Represents a scaling decision made by the AI engine."""

    def __init__(
        self,
        action: str,
        recommended_pod_count: Optional[int] = None,
        recommended_memory_increase: Optional[str] = None,
        recommended_cpu_increase: Optional[str] = None,
        confidence: float = 0.0,
        reasoning: str = "",
        urgency: str = "normal",
        estimated_cost_impact: Optional[str] = None,
    ):
        self.action = action
        self.recommended_pod_count = recommended_pod_count
        self.recommended_memory_increase = recommended_memory_increase
        self.recommended_cpu_increase = recommended_cpu_increase
        self.confidence = confidence
        self.reasoning = reasoning
        self.urgency = urgency
        self.estimated_cost_impact = estimated_cost_impact
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary format."""
        return {
            "action": self.action,
            "recommended_pod_count": self.recommended_pod_count,
            "recommended_memory_increase": self.recommended_memory_increase,
            "recommended_cpu_increase": self.recommended_cpu_increase,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "urgency": self.urgency,
            "estimated_cost_impact": self.estimated_cost_impact,
            "timestamp": self.timestamp.isoformat(),
        }


class AIScalingEngine:
    """
    AI-powered scaling decision engine.

    Uses LLM to analyze system metrics and make intelligent scaling decisions
    for Kubernetes deployments.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the AI scaling engine.

        Args:
            api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)
            model: AI model to use for analysis
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None

        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)

    def analyze_metrics(
        self, current_metrics: ScalingMetrics, historical_metrics: Optional[List[ScalingMetrics]] = None
    ) -> ScalingDecision:
        """
        Analyze current and historical metrics to make a scaling decision.

        Args:
            current_metrics: Current system metrics
            historical_metrics: Optional list of historical metrics for trend analysis

        Returns:
            ScalingDecision with recommended action
        """
        with tracer.start_as_current_span("analyze_metrics") as span:
            span.set_attribute("current_pod_count", current_metrics.current_pod_count)
            span.set_attribute("cpu_utilization", current_metrics.cpu_utilization)
            span.set_attribute("memory_utilization", current_metrics.memory_utilization)

            with scaling_analysis_latency.time():
                if not self.client:
                    # Fallback to rule-based decision if no AI client
                    decision = self._rule_based_decision(current_metrics)
                else:
                    # Use AI for decision making
                    decision = self._ai_based_decision(current_metrics, historical_metrics)

                span.set_attribute("scaling_action", decision.action)
                span.set_attribute("confidence", decision.confidence)

                # Track decision metrics
                confidence_level = (
                    "high" if decision.confidence > 0.8 else "medium" if decision.confidence > 0.5 else "low"
                )
                scaling_decisions_total.labels(decision_type=decision.action, confidence_level=confidence_level).inc()

                return decision

    def _rule_based_decision(self, metrics: ScalingMetrics) -> ScalingDecision:
        """
        Fallback rule-based scaling decision when AI is unavailable.

        Args:
            metrics: Current system metrics

        Returns:
            ScalingDecision based on simple rules
        """
        # Scale up conditions
        if metrics.cpu_utilization > 80 or metrics.memory_utilization > 85:
            if metrics.memory_utilization > 90:
                return ScalingDecision(
                    action="scale_up_vertical",
                    recommended_memory_increase="50%",
                    confidence=0.85,
                    reasoning="Memory utilization >90%, vertical scaling recommended",
                    urgency="high",
                )
            else:
                return ScalingDecision(
                    action="scale_up_horizontal",
                    recommended_pod_count=int(metrics.current_pod_count * 1.5),
                    confidence=0.80,
                    reasoning="High CPU/memory utilization detected",
                    urgency="high",
                )

        # Scale down conditions
        if metrics.cpu_utilization < 20 and metrics.memory_utilization < 30 and metrics.current_pod_count > 2:
            return ScalingDecision(
                action="scale_down_horizontal",
                recommended_pod_count=max(2, int(metrics.current_pod_count * 0.7)),
                confidence=0.75,
                reasoning="Low resource utilization, system over-provisioned",
                urgency="low",
            )

        # Maintain current state
        return ScalingDecision(
            action="maintain",
            recommended_pod_count=metrics.current_pod_count,
            confidence=0.90,
            reasoning="All metrics within acceptable ranges",
            urgency="normal",
        )

    def _ai_based_decision(
        self, current_metrics: ScalingMetrics, historical_metrics: Optional[List[ScalingMetrics]] = None
    ) -> ScalingDecision:
        """
        Use AI/LLM to analyze metrics and make scaling decision.

        Args:
            current_metrics: Current system metrics
            historical_metrics: Optional historical metrics for trend analysis

        Returns:
            AI-generated ScalingDecision
        """
        # Prepare context for the AI
        context = self._prepare_ai_context(current_metrics, historical_metrics)

        # Create the prompt
        prompt = f"""You are an expert DevOps engineer specializing in Kubernetes autoscaling and resource optimization.

Analyze the following metrics and provide a scaling recommendation:

CURRENT METRICS:
{json.dumps(current_metrics.to_dict(), indent=2)}

{context}

Based on these metrics, provide a scaling recommendation in the following JSON format:
{{
    "action": "maintain|scale_up_horizontal|scale_down_horizontal|scale_up_vertical|scale_down_vertical",
    "recommended_pod_count": <number or null>,
    "recommended_memory_increase": "<percentage or null>",
    "recommended_cpu_increase": "<percentage or null>",
    "confidence": <0.0 to 1.0>,
    "reasoning": "<detailed explanation>",
    "urgency": "low|normal|high|critical",
    "estimated_cost_impact": "<cost analysis>"
}}

Consider:
1. Current resource utilization and capacity
2. Error rates and response times
3. Queue depth and active connections
4. Trends from historical data (if available)
5. Cost optimization opportunities
6. Risk of service degradation

Respond with ONLY the JSON object, no additional text."""

        try:
            # Call the AI model
            response = self.client.messages.create(
                model=self.model, max_tokens=1024, messages=[{"role": "user", "content": prompt}]
            )

            # Parse the AI response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            decision_data = json.loads(response_text)

            return ScalingDecision(
                action=decision_data.get("action", "maintain"),
                recommended_pod_count=decision_data.get("recommended_pod_count"),
                recommended_memory_increase=decision_data.get("recommended_memory_increase"),
                recommended_cpu_increase=decision_data.get("recommended_cpu_increase"),
                confidence=decision_data.get("confidence", 0.0),
                reasoning=decision_data.get("reasoning", ""),
                urgency=decision_data.get("urgency", "normal"),
                estimated_cost_impact=decision_data.get("estimated_cost_impact"),
            )

        except Exception as e:
            # Fallback to rule-based on error
            print(f"AI analysis failed: {e}. Falling back to rule-based decision.")
            return self._rule_based_decision(current_metrics)

    def _prepare_ai_context(
        self, current_metrics: ScalingMetrics, historical_metrics: Optional[List[ScalingMetrics]] = None
    ) -> str:
        """
        Prepare additional context for AI analysis.

        Args:
            current_metrics: Current metrics
            historical_metrics: Historical metrics if available

        Returns:
            Formatted context string
        """
        context_parts = []

        if historical_metrics and len(historical_metrics) > 0:
            context_parts.append("HISTORICAL TRENDS:")

            # Calculate trends
            cpu_trend = self._calculate_trend([m.cpu_utilization for m in historical_metrics])
            memory_trend = self._calculate_trend([m.memory_utilization for m in historical_metrics])
            rps_trend = self._calculate_trend([m.request_rate for m in historical_metrics])

            context_parts.append(f"- CPU utilization trend: {cpu_trend}")
            context_parts.append(f"- Memory utilization trend: {memory_trend}")
            context_parts.append(f"- Request rate trend: {rps_trend}")

            # Add recent history
            context_parts.append("\nRECENT HISTORY (last 5 data points):")
            for i, m in enumerate(historical_metrics[-5:]):
                context_parts.append(
                    f"  {i + 1}. CPU: {m.cpu_utilization}%, Memory: {m.memory_utilization}%, RPS: {m.request_rate}"
                )

        return "\n".join(context_parts) if context_parts else ""

    def _calculate_trend(self, values: List[float]) -> str:
        """
        Calculate trend from a list of values.

        Args:
            values: List of metric values

        Returns:
            String description of trend
        """
        if len(values) < 2:
            return "insufficient data"

        # Simple trend calculation
        recent_avg = sum(values[-3:]) / min(3, len(values[-3:]))
        overall_avg = sum(values) / len(values)

        diff_percent = ((recent_avg - overall_avg) / overall_avg) * 100

        if diff_percent > 10:
            return f"increasing ({diff_percent:.1f}% above average)"
        elif diff_percent < -10:
            return f"decreasing ({abs(diff_percent):.1f}% below average)"
        else:
            return "stable"


def main():
    """Example usage of the AI Scaling Engine."""
    print("AI Scaling Engine Example")
    print("=" * 60)

    # Initialize the engine
    engine = AIScalingEngine()

    # Example 1: Normal load
    print("\n1. NORMAL LOAD SCENARIO")
    print("-" * 60)
    normal_metrics = ScalingMetrics(
        cpu_utilization=45.0,
        memory_utilization=55.0,
        request_rate=120.0,
        response_time_ms=85.0,
        error_rate=0.5,
        active_connections=450,
        queue_depth=5,
        current_pod_count=3,
    )

    decision = engine.analyze_metrics(normal_metrics)
    print(json.dumps(decision.to_dict(), indent=2))

    # Example 2: High load spike
    print("\n2. HIGH LOAD SPIKE SCENARIO")
    print("-" * 60)
    spike_metrics = ScalingMetrics(
        cpu_utilization=88.0,
        memory_utilization=85.0,
        request_rate=620.0,
        response_time_ms=920.0,
        error_rate=11.2,
        active_connections=2380,
        queue_depth=158,
        current_pod_count=3,
    )

    decision = engine.analyze_metrics(spike_metrics)
    print(json.dumps(decision.to_dict(), indent=2))

    # Example 3: Over-provisioned
    print("\n3. OVER-PROVISIONED SCENARIO")
    print("-" * 60)
    over_provisioned_metrics = ScalingMetrics(
        cpu_utilization=12.0,
        memory_utilization=22.0,
        request_rate=45.0,
        response_time_ms=35.0,
        error_rate=0.1,
        active_connections=180,
        queue_depth=0,
        current_pod_count=8,
    )

    decision = engine.analyze_metrics(over_provisioned_metrics)
    print(json.dumps(decision.to_dict(), indent=2))

    # Example 4: Memory constrained
    print("\n4. MEMORY CONSTRAINED SCENARIO")
    print("-" * 60)
    memory_constrained_metrics = ScalingMetrics(
        cpu_utilization=54.0,
        memory_utilization=96.0,
        request_rate=185.0,
        response_time_ms=495.0,
        error_rate=16.5,
        active_connections=692,
        queue_depth=145,
        current_pod_count=5,
    )

    decision = engine.analyze_metrics(memory_constrained_metrics)
    print(json.dumps(decision.to_dict(), indent=2))

    print("\n" + "=" * 60)
    print("Note: Set ANTHROPIC_API_KEY environment variable to enable AI-based decisions.")
    print("Currently using rule-based fallback logic.")


if __name__ == "__main__":
    main()
