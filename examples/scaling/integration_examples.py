"""
Integration Examples for AI-Powered Scaling

This module demonstrates how to integrate the AI Scaling Engine with
various observability platforms to collect metrics in real-time.
"""

from ai_scaling_engine import AIScalingEngine, ScalingMetrics


def prometheus_integration_example():
    """
    Example: Integrate with Prometheus metrics.

    Requires: prometheus_client
    """
    print("=" * 70)
    print("PROMETHEUS INTEGRATION EXAMPLE")
    print("=" * 70)

    try:
        from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

        # Create registry
        registry = CollectorRegistry()

        # Define metrics
        cpu_gauge = Gauge("cpu_utilization_percent", "CPU Utilization", registry=registry)
        memory_gauge = Gauge("memory_utilization_percent", "Memory Utilization", registry=registry)
        rps_gauge = Gauge("request_rate_per_second", "Request Rate", registry=registry)

        # Simulate current metrics (in production, query from Prometheus)
        cpu_gauge.set(75.0)
        memory_gauge.set(68.0)
        rps_gauge.set(450.0)

        # Create metrics object
        current_metrics = ScalingMetrics(
            cpu_utilization=75.0,
            memory_utilization=68.0,
            request_rate=450.0,
            response_time_ms=155.0,
            error_rate=2.2,
            active_connections=1100,
            queue_depth=48,
            current_pod_count=3,
        )

        # Analyze with AI engine
        engine = AIScalingEngine()
        decision = engine.analyze_metrics(current_metrics)

        print(f"\nMetrics from Prometheus:")
        print(f"  CPU: {current_metrics.cpu_utilization:.1f}%")
        print(f"  Memory: {current_metrics.memory_utilization:.1f}%")
        print(f"  RPS: {current_metrics.request_rate:.1f}")

        print(f"\nAI Decision:")
        print(f"  Action: {decision.action}")
        print(f"  Confidence: {decision.confidence:.2%}")
        print(f"  Reasoning: {decision.reasoning}")

        return decision

    except ImportError:
        print("prometheus_client not installed. Install with: pip install prometheus-client")
        return None


def cloudwatch_integration_example():
    """
    Example: Integrate with AWS CloudWatch.

    Requires: boto3
    """
    print("\n" + "=" * 70)
    print("AWS CLOUDWATCH INTEGRATION EXAMPLE")
    print("=" * 70)

    try:
        import boto3

        # Note: This is a mock example. In production, use actual AWS credentials
        print("\nNote: This is a demonstration. Configure AWS credentials for production use.")

        # Mock CloudWatch metrics (in production, use boto3 client)
        mock_metrics = {
            "CPUUtilization": {"Average": 82.5},
            "MemoryUtilization": {"Average": 75.0},
            "RequestCount": {"Sum": 15000},
        }

        print(f"\nMetrics from CloudWatch:")
        print(f"  CPU: {mock_metrics['CPUUtilization']['Average']:.1f}%")
        print(f"  Memory: {mock_metrics['MemoryUtilization']['Average']:.1f}%")
        print(f"  Requests: {mock_metrics['RequestCount']['Sum']}")

        # Convert to scaling metrics
        current_metrics = ScalingMetrics(
            cpu_utilization=mock_metrics["CPUUtilization"]["Average"],
            memory_utilization=mock_metrics["MemoryUtilization"]["Average"],
            request_rate=mock_metrics["RequestCount"]["Sum"] / 300,  # 5 min period
            response_time_ms=185.0,
            error_rate=2.8,
            active_connections=1240,
            queue_depth=62,
            current_pod_count=3,
        )

        # Analyze with AI engine
        engine = AIScalingEngine()
        decision = engine.analyze_metrics(current_metrics)

        print(f"\nAI Decision:")
        print(f"  Action: {decision.action}")
        print(f"  Confidence: {decision.confidence:.2%}")
        print(f"  Reasoning: {decision.reasoning}")

        # Production code would look like this:
        """
        cloudwatch = boto3.client('cloudwatch')
        
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/ECS',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'ServiceName', 'Value': 'my-service'}],
            StartTime=datetime.utcnow() - timedelta(minutes=5),
            EndTime=datetime.utcnow(),
            Period=60,
            Statistics=['Average']
        )
        
        cpu_utilization = response['Datapoints'][0]['Average']
        """

        return decision

    except ImportError:
        print("boto3 not installed. Install with: pip install boto3")
        return None


def azure_monitor_integration_example():
    """
    Example: Integrate with Azure Monitor.

    Requires: azure-monitor-query, azure-identity
    """
    print("\n" + "=" * 70)
    print("AZURE MONITOR INTEGRATION EXAMPLE")
    print("=" * 70)

    print("\nNote: This is a demonstration. Configure Azure credentials for production use.")

    # Mock Azure Monitor metrics
    mock_metrics = {
        "Percentage CPU": 78.0,
        "Memory Working Set": 72.0,
        "Requests Per Second": 380.0,
    }

    print(f"\nMetrics from Azure Monitor:")
    print(f"  CPU: {mock_metrics['Percentage CPU']:.1f}%")
    print(f"  Memory: {mock_metrics['Memory Working Set']:.1f}%")
    print(f"  RPS: {mock_metrics['Requests Per Second']:.1f}")

    # Convert to scaling metrics
    current_metrics = ScalingMetrics(
        cpu_utilization=mock_metrics["Percentage CPU"],
        memory_utilization=mock_metrics["Memory Working Set"],
        request_rate=mock_metrics["Requests Per Second"],
        response_time_ms=215.0,
        error_rate=3.5,
        active_connections=1370,
        queue_depth=78,
        current_pod_count=3,
    )

    # Analyze with AI engine
    engine = AIScalingEngine()
    decision = engine.analyze_metrics(current_metrics)

    print(f"\nAI Decision:")
    print(f"  Action: {decision.action}")
    print(f"  Confidence: {decision.confidence:.2%}")
    print(f"  Reasoning: {decision.reasoning}")

    # Production code would look like this:
    """
    from azure.monitor.query import MetricsQueryClient
    from azure.identity import DefaultAzureCredential

    credential = DefaultAzureCredential()
    client = MetricsQueryClient(credential)

    response = client.query_resource(
        resource_uri="<resource-id>",
        metric_names=["Percentage CPU", "Memory Working Set"],
        timespan=timedelta(minutes=5)
    )

    for metric in response.metrics:
        for time_series in metric.timeseries:
            for data_point in time_series.data:
                # Process metrics
                pass
    """

    return decision


def datadog_integration_example():
    """
    Example: Integrate with Datadog.

    Requires: datadog
    """
    print("\n" + "=" * 70)
    print("DATADOG INTEGRATION EXAMPLE")
    print("=" * 70)

    print("\nNote: This is a demonstration. Configure Datadog API keys for production use.")

    # Mock Datadog metrics
    mock_metrics = {
        "system.cpu.user": 45.2,
        "system.mem.used": 62.5,
        "nginx.net.request_per_s": 325.0,
    }

    print(f"\nMetrics from Datadog:")
    print(f"  CPU: {mock_metrics['system.cpu.user']:.1f}%")
    print(f"  Memory: {mock_metrics['system.mem.used']:.1f}%")
    print(f"  RPS: {mock_metrics['nginx.net.request_per_s']:.1f}")

    # Convert to scaling metrics
    current_metrics = ScalingMetrics(
        cpu_utilization=mock_metrics["system.cpu.user"],
        memory_utilization=mock_metrics["system.mem.used"],
        request_rate=mock_metrics["nginx.net.request_per_s"],
        response_time_ms=142.0,
        error_rate=1.6,
        active_connections=960,
        queue_depth=35,
        current_pod_count=3,
    )

    # Analyze with AI engine
    engine = AIScalingEngine()
    decision = engine.analyze_metrics(current_metrics)

    print(f"\nAI Decision:")
    print(f"  Action: {decision.action}")
    print(f"  Confidence: {decision.confidence:.2%}")
    print(f"  Reasoning: {decision.reasoning}")

    # Production code would look like this:
    """
    from datadog import initialize, api

    options = {
        'api_key': os.getenv('DATADOG_API_KEY'),
        'app_key': os.getenv('DATADOG_APP_KEY')
    }
    initialize(**options)

    # Query metrics
    end = int(time.time())
    start = end - 300  # 5 minutes ago

    query = 'avg:system.cpu.user{*}'
    result = api.Metric.query(start=start, end=end, query=query)
    """

    return decision


def main():
    """Run all integration examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "AI SCALING ENGINE - OBSERVABILITY INTEGRATIONS" + " " * 11 + "║")
    print("╚" + "=" * 68 + "╝")

    # Run all examples
    prometheus_integration_example()
    cloudwatch_integration_example()
    azure_monitor_integration_example()
    datadog_integration_example()

    print("\n" + "=" * 70)
    print("INTEGRATION EXAMPLES COMPLETE")
    print("=" * 70)
    print("\n📚 See README.md for detailed integration instructions")
    print("🔌 Configure credentials and API keys for production use")
    print("⚡ All integrations follow the same pattern:")
    print("   1. Collect metrics from observability platform")
    print("   2. Convert to ScalingMetrics object")
    print("   3. Analyze with AI Scaling Engine")
    print("   4. Apply recommendations")
    print()


if __name__ == "__main__":
    main()
