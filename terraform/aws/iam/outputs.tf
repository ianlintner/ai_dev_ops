output "ai_inference_role_arn" {
  description = "ARN of the AI Inference Service IAM role"
  value       = aws_iam_role.ai_inference_service.arn
}

output "ai_inference_role_name" {
  description = "Name of the AI Inference Service IAM role"
  value       = aws_iam_role.ai_inference_service.name
}
