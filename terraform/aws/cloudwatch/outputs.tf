output "log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.ai_services.name
}

output "log_group_arn" {
  description = "CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.ai_services.arn
}

output "dashboard_name" {
  description = "CloudWatch dashboard name"
  value       = aws_cloudwatch_dashboard.ai_services.dashboard_name
}
