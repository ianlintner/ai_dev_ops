"""
AWS Lambda function for AI inference with observability.

This example shows how to deploy AI inference as a Lambda function
with CloudWatch and X-Ray integration.
"""

import json
import os
import time
import random
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import boto3

# Patch AWS SDK
patch_all()

# Initialize clients
cloudwatch = boto3.client('cloudwatch')


@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    """
    Lambda handler for AI inference requests.
    
    Event structure:
    {
        "input": "User query text",
        "model": "gpt-4",
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 100
        }
    }
    """
    # Extract request data
    user_input = event.get('input', '')
    model_name = event.get('model', 'gpt-4')
    parameters = event.get('parameters', {})

    # Add annotations to X-Ray
    segment = xray_recorder.current_segment()
    segment.put_annotation('model_name', model_name)
    segment.put_annotation('input_length', len(user_input))

    try:
        # Perform inference
        result = perform_inference(user_input, model_name, parameters)

        # Send metrics
        send_metrics(model_name, result['latency_ms'], result['tokens_used'], True)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'result': result['output'],
                'model': model_name,
                'tokens': result['tokens_used'],
                'latency_ms': result['latency_ms']
            })
        }

    except Exception as e:
        # Track error
        segment.put_annotation('error', True)
        segment.put_metadata('error_message', str(e))

        send_metrics(model_name, 0, 0, False)

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'model': model_name
            })
        }


@xray_recorder.capture('perform_inference')
def perform_inference(user_input, model_name, parameters):
    """Perform AI model inference."""
    start_time = time.time()

    # Simulate inference
    inference_time = random.uniform(0.1, 0.5)
    time.sleep(inference_time)

    # Generate response
    output = f"AI response to: {user_input}"
    tokens_used = len(output.split())

    latency_ms = (time.time() - start_time) * 1000

    # Add metadata to X-Ray
    subsegment = xray_recorder.current_subsegment()
    subsegment.put_metadata('tokens_used', tokens_used)
    subsegment.put_metadata('latency_ms', latency_ms)

    return {
        'output': output,
        'tokens_used': tokens_used,
        'latency_ms': latency_ms
    }


def send_metrics(model_name, latency_ms, tokens, success):
    """Send custom metrics to CloudWatch."""
    try:
        metric_data = [
            {
                'MetricName': 'InferenceCount',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'ModelName', 'Value': model_name},
                    {'Name': 'Status', 'Value': 'success' if success else 'error'}
                ]
            }
        ]

        if success:
            metric_data.extend([
                {
                    'MetricName': 'InferenceLatency',
                    'Value': latency_ms,
                    'Unit': 'Milliseconds',
                    'Dimensions': [
                        {'Name': 'ModelName', 'Value': model_name}
                    ]
                },
                {
                    'MetricName': 'TokensUsed',
                    'Value': tokens,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'ModelName', 'Value': model_name}
                    ]
                }
            ])

        cloudwatch.put_metric_data(
            Namespace='AIDevOps/Lambda',
            MetricData=metric_data
        )
    except Exception as e:
        print(f"Failed to send metrics: {e}")
