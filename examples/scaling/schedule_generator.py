"""
AI-Powered Scaling Schedule Generator

This module analyzes historical metrics to identify patterns and generate
optimal scaling schedules for predictable workload variations.
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from opentelemetry import trace

from ai_scaling_engine import AIScalingEngine, ScalingMetrics

tracer = trace.get_tracer(__name__)


class ScalingSchedule:
    """Represents a time-based scaling schedule."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.schedule_entries: List[Dict[str, Any]] = []

    def add_entry(
        self, time: str, target_pods: int, reason: str, day_of_week: Optional[str] = None, confidence: float = 1.0
    ):
        """
        Add a scheduled scaling entry.

        Args:
            time: Time in HH:MM format
            target_pods: Target number of pods
            reason: Explanation for this scaling action
            day_of_week: Optional day of week (e.g., "monday", "weekend")
            confidence: Confidence level in this recommendation (0.0-1.0)
        """
        entry = {
            "time": time,
            "target_pods": target_pods,
            "reason": reason,
            "confidence": confidence,
        }
        if day_of_week:
            entry["day_of_week"] = day_of_week

        self.schedule_entries.append(entry)

    def to_dict(self) -> Dict[str, Any]:
        """Convert schedule to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "schedule_entries": sorted(self.schedule_entries, key=lambda x: x["time"]),
        }

    def to_cron_jobs(self) -> List[Dict[str, str]]:
        """
        Generate Kubernetes CronJob specifications for this schedule.

        Returns:
            List of CronJob configurations
        """
        cron_jobs = []

        for entry in self.schedule_entries:
            hour, minute = entry["time"].split(":")

            # Basic cron expression (minute hour * * *)
            cron_expr = f"{minute} {hour} * * *"

            # Adjust for day of week if specified
            if "day_of_week" in entry:
                if entry["day_of_week"].lower() == "weekend":
                    cron_expr = f"{minute} {hour} * * 0,6"  # Sunday and Saturday
                elif entry["day_of_week"].lower() == "weekday":
                    cron_expr = f"{minute} {hour} * * 1-5"  # Monday to Friday

            cron_jobs.append(
                {
                    "schedule": cron_expr,
                    "target_pods": entry["target_pods"],
                    "reason": entry["reason"],
                    "kubectl_command": f"kubectl scale deployment ai-inference-service --replicas={entry['target_pods']}",
                }
            )

        return cron_jobs


class ScheduleGenerator:
    """
    Generates optimal scaling schedules from historical metrics data.

    Analyzes patterns in historical data to identify:
    - Daily peak hours
    - Day of week variations
    - Recurring events
    - Optimal pre-scaling times
    """

    def __init__(self, scaling_engine: Optional[AIScalingEngine] = None):
        """
        Initialize the schedule generator.

        Args:
            scaling_engine: Optional AI scaling engine for enhanced analysis
        """
        self.scaling_engine = scaling_engine or AIScalingEngine()

    def analyze_patterns(self, metrics_history: List[Tuple[datetime, ScalingMetrics]]) -> Dict[str, Any]:
        """
        Analyze historical metrics to identify patterns.

        Args:
            metrics_history: List of (timestamp, metrics) tuples

        Returns:
            Dictionary with pattern analysis
        """
        with tracer.start_as_current_span("analyze_patterns") as span:
            span.set_attribute("metrics_count", len(metrics_history))

            if not metrics_history:
                return {"error": "No metrics history provided"}

            # Group metrics by hour of day
            hourly_patterns = defaultdict(list)
            daily_patterns = defaultdict(list)

            for timestamp, metrics in metrics_history:
                hour = timestamp.hour
                day_of_week = timestamp.strftime("%A")

                hourly_patterns[hour].append(metrics)
                daily_patterns[day_of_week].append(metrics)

            # Calculate average metrics per hour
            hourly_averages = {}
            for hour, metrics_list in hourly_patterns.items():
                hourly_averages[hour] = {
                    "cpu": sum(m.cpu_utilization for m in metrics_list) / len(metrics_list),
                    "memory": sum(m.memory_utilization for m in metrics_list) / len(metrics_list),
                    "rps": sum(m.request_rate for m in metrics_list) / len(metrics_list),
                    "avg_pods": sum(m.current_pod_count for m in metrics_list) / len(metrics_list),
                    "max_pods": max(m.current_pod_count for m in metrics_list),
                }

            # Calculate average metrics per day of week
            daily_averages = {}
            for day, metrics_list in daily_patterns.items():
                daily_averages[day] = {
                    "cpu": sum(m.cpu_utilization for m in metrics_list) / len(metrics_list),
                    "memory": sum(m.memory_utilization for m in metrics_list) / len(metrics_list),
                    "rps": sum(m.request_rate for m in metrics_list) / len(metrics_list),
                    "avg_pods": sum(m.current_pod_count for m in metrics_list) / len(metrics_list),
                }

            # Identify peak hours
            peak_hours = self._identify_peak_hours(hourly_averages)

            # Identify low-traffic periods
            low_hours = self._identify_low_hours(hourly_averages)

            span.set_attribute("peak_hours_count", len(peak_hours))

            return {
                "hourly_patterns": hourly_averages,
                "daily_patterns": daily_averages,
                "peak_hours": peak_hours,
                "low_traffic_hours": low_hours,
                "analysis_timestamp": datetime.utcnow().isoformat(),
            }

    def generate_schedule(
        self, metrics_history: List[Tuple[datetime, ScalingMetrics]], min_pods: int = 2, max_pods: int = 20
    ) -> ScalingSchedule:
        """
        Generate a scaling schedule from historical metrics.

        Args:
            metrics_history: List of (timestamp, metrics) tuples
            min_pods: Minimum number of pods
            max_pods: Maximum number of pods

        Returns:
            ScalingSchedule object
        """
        with tracer.start_as_current_span("generate_schedule") as span:
            # Analyze patterns
            patterns = self.analyze_patterns(metrics_history)

            if "error" in patterns:
                schedule = ScalingSchedule("error-schedule")
                return schedule

            schedule = ScalingSchedule(
                name="ai-workload-schedule", description="Generated from historical metrics analysis"
            )

            # Generate schedule entries based on hourly patterns
            hourly_averages = patterns["hourly_patterns"]

            for hour in sorted(hourly_averages.keys()):
                metrics = hourly_averages[hour]

                # Calculate recommended pods based on average load
                cpu_factor = metrics["cpu"] / 70.0  # Target 70% CPU
                memory_factor = metrics["memory"] / 80.0  # Target 80% memory

                scaling_factor = max(cpu_factor, memory_factor)
                recommended_pods = int(metrics["avg_pods"] * max(1.0, scaling_factor))

                # Clamp to min/max
                recommended_pods = max(min_pods, min(max_pods, recommended_pods))

                # Add buffer for peaks (pre-scale 30 minutes before high load)
                is_peak = hour in [h["hour"] for h in patterns["peak_hours"]]

                if is_peak:
                    # Pre-scale 30 minutes before peak hour
                    pre_hour = (hour - 1) % 24
                    pre_minute = 30
                    schedule.add_entry(
                        f"{pre_hour:02d}:{pre_minute:02d}",
                        recommended_pods,
                        f"Pre-scale for peak hour {hour}:00",
                        confidence=0.9,
                    )

                # Add entry for the hour
                schedule.add_entry(
                    f"{hour:02d}:00", recommended_pods, f"Scheduled scaling for hour {hour}", confidence=0.85
                )

            # Identify opportunities for scaling down during low traffic
            for hour_info in patterns["low_traffic_hours"]:
                hour = hour_info["hour"]
                schedule.add_entry(
                    f"{hour:02d}:00", min_pods, f"Scale down during low traffic", confidence=0.95
                )

            span.set_attribute("schedule_entries", len(schedule.schedule_entries))

            return schedule

    def generate_weekly_schedule(
        self, metrics_history: List[Tuple[datetime, ScalingMetrics]], min_pods: int = 2, max_pods: int = 20
    ) -> Dict[str, ScalingSchedule]:
        """
        Generate separate schedules for weekdays and weekends.

        Args:
            metrics_history: List of (timestamp, metrics) tuples
            min_pods: Minimum number of pods
            max_pods: Maximum number of pods

        Returns:
            Dictionary with 'weekday' and 'weekend' schedules
        """
        # Separate metrics by weekday vs weekend
        weekday_metrics = []
        weekend_metrics = []

        for timestamp, metrics in metrics_history:
            if timestamp.weekday() < 5:  # Monday = 0, Friday = 4
                weekday_metrics.append((timestamp, metrics))
            else:
                weekend_metrics.append((timestamp, metrics))

        schedules = {}

        if weekday_metrics:
            weekday_schedule = self.generate_schedule(weekday_metrics, min_pods, max_pods)
            weekday_schedule.name = "weekday-schedule"
            weekday_schedule.description = "Scaling schedule for Monday-Friday"
            schedules["weekday"] = weekday_schedule

        if weekend_metrics:
            weekend_schedule = self.generate_schedule(weekend_metrics, min_pods, max_pods)
            weekend_schedule.name = "weekend-schedule"
            weekend_schedule.description = "Scaling schedule for Saturday-Sunday"
            schedules["weekend"] = weekend_schedule

        return schedules

    def _identify_peak_hours(self, hourly_averages: Dict[int, Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Identify peak traffic hours from hourly averages.

        Args:
            hourly_averages: Dictionary of hour -> metrics

        Returns:
            List of peak hour dictionaries
        """
        if not hourly_averages:
            return []

        # Calculate overall average CPU and RPS
        avg_cpu = sum(h["cpu"] for h in hourly_averages.values()) / len(hourly_averages)
        avg_rps = sum(h["rps"] for h in hourly_averages.values()) / len(hourly_averages)

        # Identify hours significantly above average (>50% higher)
        peak_hours = []
        for hour, metrics in hourly_averages.items():
            if metrics["cpu"] > avg_cpu * 1.5 or metrics["rps"] > avg_rps * 1.5:
                peak_hours.append(
                    {"hour": hour, "cpu": metrics["cpu"], "rps": metrics["rps"], "severity": "high"}
                )

        return sorted(peak_hours, key=lambda x: x["cpu"], reverse=True)

    def _identify_low_hours(self, hourly_averages: Dict[int, Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Identify low traffic hours from hourly averages.

        Args:
            hourly_averages: Dictionary of hour -> metrics

        Returns:
            List of low traffic hour dictionaries
        """
        if not hourly_averages:
            return []

        # Calculate overall average
        avg_cpu = sum(h["cpu"] for h in hourly_averages.values()) / len(hourly_averages)
        avg_rps = sum(h["rps"] for h in hourly_averages.values()) / len(hourly_averages)

        # Identify hours significantly below average (<50% of average)
        low_hours = []
        for hour, metrics in hourly_averages.items():
            if metrics["cpu"] < avg_cpu * 0.5 and metrics["rps"] < avg_rps * 0.5:
                low_hours.append({"hour": hour, "cpu": metrics["cpu"], "rps": metrics["rps"]})

        return sorted(low_hours, key=lambda x: x["hour"])


def main():
    """Example usage of Schedule Generator."""
    print("AI-Powered Scaling Schedule Generator")
    print("=" * 70)

    generator = ScheduleGenerator()

    # Load test data
    print("\nLoading test metrics data...")
    from pathlib import Path
    script_dir = Path(__file__).parent
    test_data_path = script_dir / "test_data" / "metrics_dataset.json"
    
    with open(test_data_path, "r") as f:
        test_data = json.load(f)

    # Find the daily pattern scenario
    daily_pattern = None
    for scenario in test_data["scenarios"]:
        if scenario["scenario"] == "daily_peak_pattern":
            daily_pattern = scenario
            break

    if daily_pattern:
        print("Processing daily peak pattern data...")

        # Convert to metrics history format
        metrics_history = []
        base_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        for hour_data in daily_pattern["hourly_metrics"]:
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

        # Analyze patterns
        print("\n" + "=" * 70)
        print("PATTERN ANALYSIS")
        print("-" * 70)

        patterns = generator.analyze_patterns(metrics_history)
        print("\nPeak Hours:")
        for peak in patterns["peak_hours"][:5]:
            print(f"  Hour {peak['hour']:02d}:00 - CPU: {peak['cpu']:.1f}%, RPS: {peak['rps']:.1f}")

        print("\nLow Traffic Hours:")
        for low in patterns["low_traffic_hours"]:
            print(f"  Hour {low['hour']:02d}:00 - CPU: {low['cpu']:.1f}%, RPS: {low['rps']:.1f}")

        # Generate schedule
        print("\n" + "=" * 70)
        print("GENERATED SCALING SCHEDULE")
        print("-" * 70)

        schedule = generator.generate_schedule(metrics_history, min_pods=3, max_pods=10)

        # Show schedule (limiting to key entries for readability)
        schedule_dict = schedule.to_dict()
        print(f"\nSchedule Name: {schedule_dict['name']}")
        print(f"Description: {schedule_dict['description']}")
        print(f"\nSchedule Entries (showing first 10):")

        for i, entry in enumerate(schedule_dict["schedule_entries"][:10]):
            print(
                f"  {entry['time']} - {entry['target_pods']} pods - {entry['reason']} (confidence: {entry['confidence']:.2f})"
            )

        # Generate CronJob specifications
        print("\n" + "=" * 70)
        print("KUBERNETES CRONJOB SPECIFICATIONS (first 5)")
        print("-" * 70)

        cron_jobs = schedule.to_cron_jobs()
        for i, job in enumerate(cron_jobs[:5]):
            print(f"\nCronJob {i + 1}:")
            print(f"  Schedule: {job['schedule']}")
            print(f"  Target Pods: {job['target_pods']}")
            print(f"  Reason: {job['reason']}")
            print(f"  Command: {job['kubectl_command']}")

    else:
        print("Daily pattern scenario not found in test data")

    print("\n" + "=" * 70)
    print(f"Total schedule entries generated: {len(schedule.schedule_entries)}")


if __name__ == "__main__":
    main()
