"""
Comprehensive AI-Powered Autoscaling Example

This example demonstrates the complete workflow of using AI to manage
Kubernetes scaling, including:
1. Loading historical metrics
2. AI-powered decision making
3. HPA configuration management
4. Schedule generation for predictable patterns
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ai_scaling_engine import AIScalingEngine, ScalingMetrics
from k8s_hpa_manager import HPAConfiguration, K8sHPAManager
from schedule_generator import ScheduleGenerator


def load_test_scenario(scenario_name: str) -> dict:
    """Load a test scenario from the metrics dataset."""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    test_data_path = script_dir / "test_data" / "metrics_dataset.json"
    
    with open(test_data_path, "r") as f:
        data = json.load(f)

    for scenario in data["scenarios"]:
        if scenario["scenario"] == scenario_name:
            return scenario

    return None


def demo_real_time_scaling_decision():
    """Demonstrate real-time scaling decision based on current metrics."""
    print("=" * 80)
    print("DEMO 1: REAL-TIME SCALING DECISIONS")
    print("=" * 80)

    engine = AIScalingEngine()

    # Load high load spike scenario
    scenario = load_test_scenario("high_load_spike")
    if not scenario:
        print("Error: Could not load test scenario")
        return

    print(f"\nScenario: {scenario['description']}")
    print(f"Duration: {scenario['duration_minutes']} minutes")

    # Get the last data point (peak load)
    metrics_data = scenario["metrics"]
    idx = -1  # Last data point

    current_metrics = ScalingMetrics(
        cpu_utilization=metrics_data["cpu_utilization_percent"][idx],
        memory_utilization=metrics_data["memory_utilization_percent"][idx],
        request_rate=metrics_data["request_rate_per_second"][idx],
        response_time_ms=metrics_data["response_time_ms"][idx],
        error_rate=metrics_data["error_rate_percent"][idx],
        active_connections=metrics_data["active_connections"][idx],
        queue_depth=metrics_data["queue_depth"][idx],
        current_pod_count=metrics_data["pod_count"][idx],
    )

    print("\nCurrent Metrics:")
    print(json.dumps(current_metrics.to_dict(), indent=2))

    # Get AI decision
    print("\nAnalyzing with AI Scaling Engine...")
    decision = engine.analyze_metrics(current_metrics)

    print("\nAI Decision:")
    print(json.dumps(decision.to_dict(), indent=2))

    print(f"\n✓ Recommendation: {decision.action}")
    print(f"✓ Confidence: {decision.confidence:.2%}")
    print(f"✓ Reasoning: {decision.reasoning}")


def demo_hpa_management():
    """Demonstrate HPA configuration management."""
    print("\n\n" + "=" * 80)
    print("DEMO 2: KUBERNETES HPA MANAGEMENT")
    print("=" * 80)

    # Initialize HPA manager in dry-run mode
    manager = K8sHPAManager(dry_run=True)

    # Create initial HPA configuration
    hpa_config = HPAConfiguration(
        name="ai-inference-hpa", namespace="ai-services", min_replicas=3, max_replicas=20
    )

    print("\nInitial HPA Configuration:")
    print(json.dumps(hpa_config.to_dict(), indent=2))

    # Load over-provisioned scenario
    scenario = load_test_scenario("over_provisioned")
    if not scenario:
        print("Error: Could not load test scenario")
        return

    print(f"\n\nScenario: {scenario['description']}")

    # Create metrics from scenario
    metrics_data = scenario["metrics"]
    current_metrics = ScalingMetrics(
        cpu_utilization=metrics_data["cpu_utilization_percent"][0],
        memory_utilization=metrics_data["memory_utilization_percent"][0],
        request_rate=metrics_data["request_rate_per_second"][0],
        response_time_ms=metrics_data["response_time_ms"][0],
        error_rate=metrics_data["error_rate_percent"][0],
        active_connections=metrics_data["active_connections"][0],
        queue_depth=metrics_data["queue_depth"][0],
        current_pod_count=metrics_data["pod_count"][0],
    )

    # Update HPA based on metrics
    print("\nUpdating HPA configuration based on metrics...")
    result = manager.update_hpa_from_metrics(hpa_config, current_metrics)

    print("\nUpdate Result:")
    print(json.dumps(result, indent=2))

    print("\nUpdated HPA Configuration:")
    print(json.dumps(hpa_config.to_dict(), indent=2))


def demo_schedule_generation():
    """Demonstrate schedule generation from historical data."""
    print("\n\n" + "=" * 80)
    print("DEMO 3: SCALING SCHEDULE GENERATION")
    print("=" * 80)

    generator = ScheduleGenerator()

    # Load daily pattern scenario
    scenario = load_test_scenario("daily_peak_pattern")
    if not scenario:
        print("Error: Could not load test scenario")
        return

    print(f"\nScenario: {scenario['description']}")
    print(f"Duration: {scenario['duration_minutes']} minutes (24 hours)")

    # Convert to metrics history format
    metrics_history = []
    base_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    for hour_data in scenario["hourly_metrics"]:
        timestamp = base_time + timedelta(hours=hour_data["hour"])
        metrics = ScalingMetrics(
            cpu_utilization=hour_data["cpu"],
            memory_utilization=hour_data["memory"],
            request_rate=hour_data["rps"],
            response_time_ms=hour_data["response_ms"],
            error_rate=0.5,
            active_connections=hour_data["rps"] * 4,
            queue_depth=5,
            current_pod_count=hour_data["pods"],
            timestamp=timestamp,
        )
        metrics_history.append((timestamp, metrics))

    print(f"\nAnalyzing {len(metrics_history)} hours of metrics data...")

    # Analyze patterns
    patterns = generator.analyze_patterns(metrics_history)

    print("\n📊 Pattern Analysis:")
    print(f"  Peak Hours Identified: {len(patterns['peak_hours'])}")
    print(f"  Low Traffic Hours: {len(patterns['low_traffic_hours'])}")

    print("\n  Top 3 Peak Hours:")
    for i, peak in enumerate(patterns["peak_hours"][:3], 1):
        print(f"    {i}. Hour {peak['hour']:02d}:00 - CPU: {peak['cpu']:.1f}%, RPS: {peak['rps']:.1f}")

    # Generate schedule
    print("\n📅 Generating Scaling Schedule...")
    schedule = generator.generate_schedule(metrics_history, min_pods=3, max_pods=10)

    schedule_dict = schedule.to_dict()
    print(f"\n  Schedule Name: {schedule_dict['name']}")
    print(f"  Total Entries: {len(schedule_dict['schedule_entries'])}")

    print("\n  Sample Schedule Entries:")
    # Show morning, afternoon, and evening entries
    sample_times = ["06:00", "08:00", "12:00", "17:00", "19:00", "23:00"]
    for entry in schedule_dict["schedule_entries"]:
        if entry["time"] in sample_times:
            print(
                f"    {entry['time']} → {entry['target_pods']} pods - {entry['reason']} (confidence: {entry['confidence']:.0%})"
            )

    # Show CronJob examples
    print("\n  Kubernetes CronJob Examples:")
    cron_jobs = schedule.to_cron_jobs()
    for i, job in enumerate(cron_jobs[:3], 1):
        print(f"\n    CronJob {i}:")
        print(f"      Schedule: {job['schedule']}")
        print(f"      Target: {job['target_pods']} pods")
        print(f"      Command: {job['kubectl_command']}")


def demo_cost_optimization():
    """Demonstrate cost optimization through intelligent scaling."""
    print("\n\n" + "=" * 80)
    print("DEMO 4: COST OPTIMIZATION ANALYSIS")
    print("=" * 80)

    # Compare weekend vs weekday scaling
    scenarios = {
        "weekday": load_test_scenario("daily_peak_pattern"),
        "weekend": load_test_scenario("weekend_low_traffic"),
    }

    print("\n💰 Cost Optimization Opportunity Analysis:\n")

    for period, scenario in scenarios.items():
        if not scenario:
            continue

        # Handle both metric structures (daily pattern uses hourly_metrics)
        if "hourly_metrics" in scenario:
            metrics_list = scenario["hourly_metrics"]
            avg_pods = sum(h["pods"] for h in metrics_list) / len(metrics_list)
            avg_cpu = sum(h["cpu"] for h in metrics_list) / len(metrics_list)
            avg_rps = sum(h["rps"] for h in metrics_list) / len(metrics_list)
        else:
            metrics = scenario["metrics"]
            avg_pods = sum(metrics["pod_count"]) / len(metrics["pod_count"])
            avg_cpu = sum(metrics["cpu_utilization_percent"]) / len(metrics["cpu_utilization_percent"])
            avg_rps = sum(metrics["request_rate_per_second"]) / len(metrics["request_rate_per_second"])

        print(f"  {period.upper()}:")
        print(f"    Average Pods: {avg_pods:.1f}")
        print(f"    Average CPU: {avg_cpu:.1f}%")
        print(f"    Average RPS: {avg_rps:.1f}")
        print(f"    Recommended: {scenario['recommended_action']}")
        print(f"    Target Pods: {scenario.get('recommended_pod_count', 'N/A')}")
        print()

    print("  💡 Insights:")
    print("    • Weekend traffic is ~60% lower than weekday")
    print("    • Scaling down on weekends can reduce costs by ~40%")
    print("    • Schedule-based scaling provides predictable cost management")
    print("    • AI recommendations optimize both cost and performance")


def demo_vertical_scaling():
    """Demonstrate vertical scaling recommendations."""
    print("\n\n" + "=" * 80)
    print("DEMO 5: VERTICAL SCALING RECOMMENDATIONS")
    print("=" * 80)

    engine = AIScalingEngine()

    # Load memory constrained scenario
    scenario = load_test_scenario("memory_constrained")
    if not scenario:
        print("Error: Could not load test scenario")
        return

    print(f"\nScenario: {scenario['description']}")

    metrics_data = scenario["metrics"]
    current_metrics = ScalingMetrics(
        cpu_utilization=metrics_data["cpu_utilization_percent"][-1],
        memory_utilization=metrics_data["memory_utilization_percent"][-1],
        request_rate=metrics_data["request_rate_per_second"][-1],
        response_time_ms=metrics_data["response_time_ms"][-1],
        error_rate=metrics_data["error_rate_percent"][-1],
        active_connections=metrics_data["active_connections"][-1],
        queue_depth=metrics_data["queue_depth"][-1],
        current_pod_count=metrics_data["pod_count"][-1],
    )

    print("\nCritical Metrics:")
    print(f"  CPU: {current_metrics.cpu_utilization}%")
    print(f"  Memory: {current_metrics.memory_utilization}%")
    print(f"  Error Rate: {current_metrics.error_rate}%")
    print(f"  Response Time: {current_metrics.response_time_ms}ms")

    decision = engine.analyze_metrics(current_metrics)

    print("\n🔧 Vertical Scaling Recommendation:")
    print(json.dumps(decision.to_dict(), indent=2))

    print(f"\n✓ Action: {decision.action}")
    print(f"✓ Memory Increase: {decision.recommended_memory_increase}")
    print(f"✓ Reasoning: {decision.reasoning}")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "AI-POWERED KUBERNETES AUTOSCALING DEMO" + " " * 24 + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Comprehensive demonstration of AI-driven scaling decisions," + " " * 16 + "║")
    print("║" + "  HPA management, schedule generation, and cost optimization" + " " * 15 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        demo_real_time_scaling_decision()
        demo_hpa_management()
        demo_schedule_generation()
        demo_cost_optimization()
        demo_vertical_scaling()

        print("\n\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)
        print("\n✓ All demonstrations completed successfully!")
        print("\n📚 For more information, see README.md")
        print("🔧 To integrate with your cluster, set dry_run=False in K8sHPAManager")
        print("🤖 To use AI-powered decisions, set ANTHROPIC_API_KEY environment variable")
        print()

    except FileNotFoundError as e:
        print(f"\n❌ Error: Could not find test data file: {e}")
        print("   Make sure you're running from the examples/scaling directory")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
