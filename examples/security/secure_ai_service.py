"""
Security best practices for AI services.

This example demonstrates:
- API key management
- Rate limiting
- PII detection and masking
- Input validation
- Audit logging
"""

import os
import re
import time
import hashlib
import json
from datetime import datetime, timedelta
from collections import defaultdict
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

# Configure OpenTelemetry
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)


class PIIDetector:
    """Detect and mask personally identifiable information."""

    # Patterns for common PII
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    }

    @staticmethod
    def detect_pii(text):
        """Detect PII in text."""
        detections = {}
        for pii_type, pattern in PIIDetector.PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detections[pii_type] = matches
        return detections

    @staticmethod
    def mask_pii(text):
        """Mask PII in text."""
        masked_text = text

        # Mask emails
        masked_text = re.sub(
            PIIDetector.PATTERNS['email'],
            '[EMAIL_REDACTED]',
            masked_text
        )

        # Mask phone numbers
        masked_text = re.sub(
            PIIDetector.PATTERNS['phone'],
            '[PHONE_REDACTED]',
            masked_text
        )

        # Mask SSN
        masked_text = re.sub(
            PIIDetector.PATTERNS['ssn'],
            '[SSN_REDACTED]',
            masked_text
        )

        # Mask credit cards
        masked_text = re.sub(
            PIIDetector.PATTERNS['credit_card'],
            '[CARD_REDACTED]',
            masked_text
        )

        return masked_text


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, requests_per_minute=60, burst=10):
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.buckets = defaultdict(lambda: {
            'tokens': burst,
            'last_update': time.time()
        })

    def _refill_bucket(self, bucket):
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - bucket['last_update']
        tokens_to_add = elapsed * (self.requests_per_minute / 60.0)

        bucket['tokens'] = min(
            self.burst,
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_update'] = now

    def is_allowed(self, identifier):
        """Check if request is allowed."""
        bucket = self.buckets[identifier]
        self._refill_bucket(bucket)

        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True, bucket['tokens']

        return False, 0


class AuditLogger:
    """Audit logger for security events."""

    def __init__(self, log_file='audit.log'):
        self.log_file = log_file

    def log_event(self, event_type, user_id, details):
        """Log security event."""
        event = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'user_id': user_id,
            'details': details
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')


class SecureAIService:
    """AI service with security best practices."""

    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_minute=100, burst=20)
        self.pii_detector = PIIDetector()
        self.audit_logger = AuditLogger()
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self):
        """Load API keys from secure storage."""
        # In production, load from secrets manager
        return {
            hashlib.sha256(b'test-api-key-1').hexdigest(): {
                'user_id': 'user-1',
                'tier': 'premium',
                'permissions': ['inference', 'streaming']
            }
        }

    def _validate_api_key(self, api_key):
        """Validate API key."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return self.api_keys.get(key_hash)

    def _validate_input(self, text, max_length=5000):
        """Validate user input."""
        if not text or not isinstance(text, str):
            raise ValueError("Invalid input: text must be a non-empty string")

        if len(text) > max_length:
            raise ValueError(f"Input too long: maximum {max_length} characters")

        # Check for malicious patterns
        dangerous_patterns = [
            r'<script>',
            r'javascript:',
            r'onerror=',
            r'onclick=',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError("Potentially malicious input detected")

        return True

    @tracer.start_as_current_span("secure_inference")
    def secure_inference(self, api_key, user_input, model='gpt-4'):
        """Perform inference with security controls."""
        span = trace.get_current_span()

        # 1. API Key Authentication
        user_info = self._validate_api_key(api_key)
        if not user_info:
            span.set_attribute("security.auth_failed", True)
            self.audit_logger.log_event(
                'AUTH_FAILED',
                'unknown',
                {'reason': 'Invalid API key'}
            )
            raise PermissionError("Invalid API key")

        user_id = user_info['user_id']
        span.set_attribute("user.id", user_id)
        span.set_attribute("user.tier", user_info['tier'])

        # 2. Rate Limiting
        allowed, remaining = self.rate_limiter.is_allowed(user_id)
        span.set_attribute("rate_limit.allowed", allowed)
        span.set_attribute("rate_limit.remaining", remaining)

        if not allowed:
            self.audit_logger.log_event(
                'RATE_LIMIT_EXCEEDED',
                user_id,
                {'endpoint': 'inference'}
            )
            raise PermissionError("Rate limit exceeded")

        # 3. Input Validation
        try:
            self._validate_input(user_input)
        except ValueError as e:
            span.set_attribute("validation.failed", True)
            self.audit_logger.log_event(
                'VALIDATION_FAILED',
                user_id,
                {'reason': str(e)}
            )
            raise

        # 4. PII Detection
        pii_detected = self.pii_detector.detect_pii(user_input)
        if pii_detected:
            span.set_attribute("pii.detected", True)
            span.set_attribute("pii.types", list(pii_detected.keys()))

            self.audit_logger.log_event(
                'PII_DETECTED',
                user_id,
                {
                    'pii_types': list(pii_detected.keys()),
                    'pii_count': sum(len(v) for v in pii_detected.values())
                }
            )

            # Mask PII in logs and traces
            masked_input = self.pii_detector.mask_pii(user_input)
            span.set_attribute("input.masked", masked_input[:100])
        else:
            span.set_attribute("pii.detected", False)
            span.set_attribute("input.text", user_input[:100])

        # 5. Perform Inference
        result = self._perform_inference(user_input, model)

        # 6. Audit Logging
        self.audit_logger.log_event(
            'INFERENCE_SUCCESS',
            user_id,
            {
                'model': model,
                'input_length': len(user_input),
                'pii_detected': len(pii_detected) > 0,
                'tokens_used': result['tokens']
            }
        )

        return result

    def _perform_inference(self, user_input, model):
        """Perform actual AI inference (mock)."""
        time.sleep(0.2)

        return {
            'result': f"Secure response to: {user_input[:30]}...",
            'model': model,
            'tokens': 50,
            'timestamp': time.time()
        }


if __name__ == "__main__":
    print("Secure AI Service Example")
    print("=" * 50)

    service = SecureAIService()

    # Test 1: Valid request
    print("\n=== Test 1: Valid Request ===")
    try:
        result = service.secure_inference(
            'test-api-key-1',
            'What is machine learning?',
            'gpt-4'
        )
        print(f"Success: {result['result']}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Request with PII
    print("\n=== Test 2: Request with PII ===")
    try:
        result = service.secure_inference(
            'test-api-key-1',
            'My email is john@example.com and phone is 555-123-4567',
            'gpt-4'
        )
        print(f"Success: {result['result']}")
        print("PII was detected and logged")
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Invalid API key
    print("\n=== Test 3: Invalid API Key ===")
    try:
        result = service.secure_inference(
            'invalid-key',
            'Test query',
            'gpt-4'
        )
    except PermissionError as e:
        print(f"Expected error: {e}")

    # Test 4: Rate limiting
    print("\n=== Test 4: Rate Limiting ===")
    for i in range(22):  # Exceed burst limit of 20
        try:
            result = service.secure_inference(
                'test-api-key-1',
                f'Query {i}',
                'gpt-4'
            )
            print(f"Request {i}: Success")
        except PermissionError as e:
            print(f"Request {i}: Rate limited")
            break

    time.sleep(2)  # Allow spans to export
    print("\n" + "=" * 50)
    print("Security example completed")
    print("Check audit.log for security events")
