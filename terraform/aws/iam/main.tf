# IAM Roles for AI Services

# IAM Role for AI Inference Service
resource "aws_iam_role" "ai_inference_service" {
  name = "${var.environment}-ai-inference-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = var.eks_oidc_provider_arn
        }
        Condition = {
          StringEquals = {
            "${replace(var.eks_oidc_provider_arn, "/^(.*provider/)/", "")}:sub" : "system:serviceaccount:ai-services:ai-inference"
            "${replace(var.eks_oidc_provider_arn, "/^(.*provider/)/", "")}:aud" : "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Name = "${var.environment}-ai-inference-service-role"
  }
}

# Policy for CloudWatch Logs
resource "aws_iam_policy" "cloudwatch_logs" {
  name        = "${var.environment}-ai-cloudwatch-logs-policy"
  description = "Policy for AI services to write CloudWatch logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:*:*:log-group:/aws/ai-devops/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ai_inference_cloudwatch" {
  role       = aws_iam_role.ai_inference_service.name
  policy_arn = aws_iam_policy.cloudwatch_logs.arn
}

# Policy for CloudWatch Metrics
resource "aws_iam_policy" "cloudwatch_metrics" {
  name        = "${var.environment}-ai-cloudwatch-metrics-policy"
  description = "Policy for AI services to publish CloudWatch metrics"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "cloudwatch:namespace" = "AIDevOps"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ai_inference_metrics" {
  role       = aws_iam_role.ai_inference_service.name
  policy_arn = aws_iam_policy.cloudwatch_metrics.arn
}

# Policy for X-Ray Tracing
resource "aws_iam_policy" "xray" {
  name        = "${var.environment}-ai-xray-policy"
  description = "Policy for AI services to send X-Ray traces"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "xray:GetSamplingRules",
          "xray:GetSamplingTargets",
          "xray:GetSamplingStatisticSummaries"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ai_inference_xray" {
  role       = aws_iam_role.ai_inference_service.name
  policy_arn = aws_iam_policy.xray.arn
}

# Policy for Secrets Manager (for API keys)
resource "aws_iam_policy" "secrets_manager" {
  name        = "${var.environment}-ai-secrets-policy"
  description = "Policy for AI services to read secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = "arn:aws:secretsmanager:*:*:secret:/ai-devops/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ai_inference_secrets" {
  role       = aws_iam_role.ai_inference_service.name
  policy_arn = aws_iam_policy.secrets_manager.arn
}
