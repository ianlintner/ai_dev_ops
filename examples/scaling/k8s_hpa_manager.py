"""
Kubernetes HPA Manager with AI-Powered Decision Making

This module manages Kubernetes Horizontal Pod Autoscaler (HPA) configurations
using AI-driven scaling decisions.
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml
from ai_scaling_engine import AIScalingEngine, ScalingDecision, ScalingMetrics
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class HPAConfiguration:
    """Represents a Kubernetes HPA configuration."""

    def __init__(
        self,
        name: str,
        namespace: str,
        min_replicas: int,
        max_replicas: int,
        target_cpu_utilization: int = 70,
        target_memory_utilization: int = 80,
    ):
        if min_replicas < 1:
            raise ValueError("min_replicas must be at least 1")
        if max_replicas < min_replicas:
            raise ValueError("max_replicas must be >= min_replicas")
        if not 1 <= target_cpu_utilization <= 100:
            raise ValueError("target_cpu_utilization must be between 1 and 100")
        if not 1 <= target_memory_utilization <= 100:
            raise ValueError("target_memory_utilization must be between 1 and 100")

        self.name = name
        self.namespace = namespace
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.target_cpu_utilization = target_cpu_utilization
        self.target_memory_utilization = target_memory_utilization

    def to_dict(self) -> Dict[str, Any]:
        """Convert HPA config to dictionary format."""
        return {
            "name": self.name,
            "namespace": self.namespace,
            "min_replicas": self.min_replicas,
            "max_replicas": self.max_replicas,
            "target_cpu_utilization": self.target_cpu_utilization,
            "target_memory_utilization": self.target_memory_utilization,
        }

    def to_yaml(self) -> str:
        """Generate Kubernetes YAML for this HPA configuration."""
        config = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {"name": self.name, "namespace": self.namespace},
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": self.name.replace("-hpa", ""),
                },
                "minReplicas": self.min_replicas,
                "maxReplicas": self.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {"type": "Utilization", "averageUtilization": self.target_cpu_utilization},
                        },
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": self.target_memory_utilization,
                            },
                        },
                    },
                ],
                "behavior": {
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [
                            {"type": "Percent", "value": 50, "periodSeconds": 60},
                            {"type": "Pods", "value": 2, "periodSeconds": 60},
                        ],
                        "selectPolicy": "Min",
                    },
                    "scaleUp": {
                        "stabilizationWindowSeconds": 0,
                        "policies": [
                            {"type": "Percent", "value": 100, "periodSeconds": 15},
                            {"type": "Pods", "value": 4, "periodSeconds": 15},
                        ],
                        "selectPolicy": "Max",
                    },
                },
            },
        }
        return yaml.dump(config, default_flow_style=False)


class K8sHPAManager:
    """
    Manages Kubernetes HPA configurations using AI-powered scaling decisions.

    This class integrates with the AI Scaling Engine to automatically update
    HPA min/max replica counts based on observed metrics and AI recommendations.
    """

    def __init__(self, scaling_engine: Optional[AIScalingEngine] = None, dry_run: bool = True):
        """
        Initialize the HPA Manager.

        Args:
            scaling_engine: AI scaling engine instance (creates new one if None)
            dry_run: If True, only simulates changes without applying them
        """
        self.scaling_engine = scaling_engine or AIScalingEngine()
        self.dry_run = dry_run
        self.applied_changes: List[Dict[str, Any]] = []

    def update_hpa_from_metrics(
        self,
        hpa_config: HPAConfiguration,
        current_metrics: ScalingMetrics,
        historical_metrics: Optional[List[ScalingMetrics]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze metrics and update HPA configuration accordingly.

        Args:
            hpa_config: Current HPA configuration
            current_metrics: Current system metrics
            historical_metrics: Optional historical metrics

        Returns:
            Dictionary with update details
        """
        with tracer.start_as_current_span("update_hpa_from_metrics") as span:
            span.set_attribute("hpa_name", hpa_config.name)
            span.set_attribute("current_min_replicas", hpa_config.min_replicas)
            span.set_attribute("current_max_replicas", hpa_config.max_replicas)

            # Get AI recommendation
            decision = self.scaling_engine.analyze_metrics(current_metrics, historical_metrics)

            span.set_attribute("ai_decision", decision.action)
            span.set_attribute("ai_confidence", decision.confidence)

            # Determine HPA updates based on decision
            update_result = self._apply_decision_to_hpa(hpa_config, decision, current_metrics)

            span.set_attribute("update_applied", update_result["applied"])

            return update_result

    def _apply_decision_to_hpa(
        self, hpa_config: HPAConfiguration, decision: ScalingDecision, current_metrics: ScalingMetrics
    ) -> Dict[str, Any]:
        """
        Apply AI scaling decision to HPA configuration.

        Args:
            hpa_config: HPA configuration to update
            decision: Scaling decision from AI engine
            current_metrics: Current metrics

        Returns:
            Dictionary with update details
        """
        result = {
            "hpa_name": hpa_config.name,
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision.to_dict(),
            "changes": {},
            "applied": False,
            "dry_run": self.dry_run,
        }

        original_min = hpa_config.min_replicas
        original_max = hpa_config.max_replicas

        # Apply changes based on decision type
        if decision.action == "scale_up_horizontal":
            if decision.recommended_pod_count:
                # Increase max replicas to accommodate scale up
                new_max = max(decision.recommended_pod_count + 5, hpa_config.max_replicas)
                new_min = max(hpa_config.min_replicas, int(decision.recommended_pod_count * 0.5))

                result["changes"]["min_replicas"] = {"old": original_min, "new": new_min}
                result["changes"]["max_replicas"] = {"old": original_max, "new": new_max}

                hpa_config.min_replicas = new_min
                hpa_config.max_replicas = new_max

        elif decision.action == "scale_down_horizontal":
            if decision.recommended_pod_count:
                # Decrease max replicas for cost optimization
                new_max = decision.recommended_pod_count + 3
                new_min = max(2, decision.recommended_pod_count - 1)

                result["changes"]["min_replicas"] = {"old": original_min, "new": new_min}
                result["changes"]["max_replicas"] = {"old": original_max, "new": new_max}

                hpa_config.min_replicas = new_min
                hpa_config.max_replicas = new_max

        elif decision.action in ["scale_up_vertical", "scale_down_vertical"]:
            # Vertical scaling requires updating deployment resources, not HPA
            result["note"] = "Vertical scaling requires deployment resource updates, not HPA changes"
            result["recommendation"] = {
                "memory_increase": decision.recommended_memory_increase,
                "cpu_increase": decision.recommended_cpu_increase,
            }

        elif decision.action == "maintain":
            result["note"] = "No HPA changes needed, current configuration is appropriate"

        # Apply changes if not in dry-run mode and changes were made
        if result["changes"] and not self.dry_run:
            apply_success = self._apply_hpa_to_cluster(hpa_config)
            result["applied"] = apply_success
        elif result["changes"]:
            result["note"] = "Dry-run mode: Changes not applied to cluster"

        self.applied_changes.append(result)

        return result

    def _apply_hpa_to_cluster(self, hpa_config: HPAConfiguration) -> bool:
        """
        Apply HPA configuration to Kubernetes cluster.

        Args:
            hpa_config: HPA configuration to apply

        Returns:
            True if successful, False otherwise
        """
        temp_file = None
        try:
            # Generate YAML
            yaml_content = hpa_config.to_yaml()

            # Write to temporary file using tempfile for security
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                f.write(yaml_content)
                temp_file = f.name

            # Apply using kubectl
            result = subprocess.run(["kubectl", "apply", "-f", temp_file], capture_output=True, text=True, timeout=30)

            return result.returncode == 0

        except Exception as e:
            print(f"Error applying HPA to cluster: {e}")
            return False
        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as cleanup_err:
                    print(f"Warning: Failed to remove temp file {temp_file}: {cleanup_err}")

    def get_current_hpa(self, name: str, namespace: str = "default") -> Optional[HPAConfiguration]:
        """
        Retrieve current HPA configuration from cluster.

        Args:
            name: HPA name
            namespace: Kubernetes namespace

        Returns:
            HPAConfiguration if found, None otherwise
        """
        try:
            result = subprocess.run(
                ["kubectl", "get", "hpa", name, "-n", namespace, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return None

            hpa_data = json.loads(result.stdout)

            return HPAConfiguration(
                name=hpa_data["metadata"]["name"],
                namespace=hpa_data["metadata"]["namespace"],
                min_replicas=hpa_data["spec"]["minReplicas"],
                max_replicas=hpa_data["spec"]["maxReplicas"],
            )

        except Exception as e:
            print(f"Error retrieving HPA from cluster: {e}")
            return None

    def generate_hpa_recommendations(
        self, metrics_history: List[ScalingMetrics], hpa_name: str = "ai-inference-hpa", namespace: str = "ai-services"
    ) -> Dict[str, Any]:
        """
        Generate HPA configuration recommendations based on historical metrics.

        Args:
            metrics_history: List of historical metrics
            hpa_name: Name for the HPA
            namespace: Kubernetes namespace

        Returns:
            Dictionary with recommended HPA configuration
        """
        if not metrics_history:
            return {"error": "No metrics history provided"}

        # Analyze trends
        max_cpu = max(m.cpu_utilization for m in metrics_history)
        max_memory = max(m.memory_utilization for m in metrics_history)
        max_pods = max(m.current_pod_count for m in metrics_history)
        avg_pods = sum(m.current_pod_count for m in metrics_history) / len(metrics_history)

        # Calculate recommended min/max
        recommended_min = max(2, int(avg_pods * 0.7))
        recommended_max = max(int(max_pods * 1.5), recommended_min + 5)

        # Adjust target utilizations based on observed patterns
        target_cpu = 70
        target_memory = 80

        if max_cpu > 90:
            target_cpu = 65  # Lower threshold if we've seen high CPU
        if max_memory > 90:
            target_memory = 75  # Lower threshold if we've seen high memory

        recommendation = {
            "hpa_name": hpa_name,
            "namespace": namespace,
            "recommended_config": {
                "min_replicas": recommended_min,
                "max_replicas": recommended_max,
                "target_cpu_utilization": target_cpu,
                "target_memory_utilization": target_memory,
            },
            "analysis": {
                "max_cpu_observed": max_cpu,
                "max_memory_observed": max_memory,
                "max_pods_used": max_pods,
                "avg_pods_used": round(avg_pods, 2),
            },
            "reasoning": f"Based on {len(metrics_history)} data points: "
            f"Max CPU {max_cpu}%, Max Memory {max_memory}%, "
            f"recommending min={recommended_min} max={recommended_max} pods",
        }

        return recommendation


def main():
    """Example usage of K8s HPA Manager."""
    print("Kubernetes HPA Manager with AI-Powered Scaling")
    print("=" * 70)

    # Initialize manager in dry-run mode
    manager = K8sHPAManager(dry_run=True)

    # Example HPA configuration
    hpa_config = HPAConfiguration(
        name="ai-inference-hpa", namespace="ai-services", min_replicas=3, max_replicas=20, target_cpu_utilization=70
    )

    print("\nInitial HPA Configuration:")
    print(json.dumps(hpa_config.to_dict(), indent=2))

    # Test Scenario 1: High load requiring scale up
    print("\n" + "=" * 70)
    print("SCENARIO 1: High Load - Scale Up Required")
    print("-" * 70)

    high_load_metrics = ScalingMetrics(
        cpu_utilization=88.0,
        memory_utilization=85.0,
        request_rate=620.0,
        response_time_ms=920.0,
        error_rate=11.2,
        active_connections=2380,
        queue_depth=158,
        current_pod_count=3,
    )

    update_result = manager.update_hpa_from_metrics(hpa_config, high_load_metrics)
    print(json.dumps(update_result, indent=2))

    # Test Scenario 2: Over-provisioned requiring scale down
    print("\n" + "=" * 70)
    print("SCENARIO 2: Over-Provisioned - Scale Down Opportunity")
    print("-" * 70)

    low_load_metrics = ScalingMetrics(
        cpu_utilization=12.0,
        memory_utilization=22.0,
        request_rate=45.0,
        response_time_ms=35.0,
        error_rate=0.1,
        active_connections=180,
        queue_depth=0,
        current_pod_count=8,
    )

    # Reset HPA config
    hpa_config = HPAConfiguration(name="ai-inference-hpa", namespace="ai-services", min_replicas=5, max_replicas=20)

    update_result = manager.update_hpa_from_metrics(hpa_config, low_load_metrics)
    print(json.dumps(update_result, indent=2))

    # Test Scenario 3: Generate recommendations from history
    print("\n" + "=" * 70)
    print("SCENARIO 3: Historical Analysis - HPA Recommendations")
    print("-" * 70)

    # Simulate 24 hours of metrics
    historical_metrics = [
        ScalingMetrics(45, 55, 120, 85, 0.5, 450, 5, 3),
        ScalingMetrics(72, 78, 420, 185, 2.2, 1100, 48, 3),
        ScalingMetrics(85, 88, 580, 285, 4.2, 1480, 95, 8),
        ScalingMetrics(78, 82, 480, 215, 3.5, 1370, 78, 8),
        ScalingMetrics(62, 68, 320, 142, 1.6, 960, 35, 5),
        ScalingMetrics(45, 52, 185, 95, 0.7, 680, 12, 4),
    ]

    recommendations = manager.generate_hpa_recommendations(historical_metrics)
    print(json.dumps(recommendations, indent=2))

    print("\n" + "=" * 70)
    print("Note: Running in DRY-RUN mode. Set dry_run=False to apply changes.")
    print("      Requires kubectl and cluster access to apply HPA configurations.")


if __name__ == "__main__":
    main()
