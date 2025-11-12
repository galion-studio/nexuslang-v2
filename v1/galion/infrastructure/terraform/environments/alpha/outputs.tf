# Outputs for Alpha Environment

output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "ecs_cluster_name" {
  description = "ECS Cluster name"
  value       = module.compute.ecs_cluster_name
}

output "ecs_cluster_arn" {
  description = "ECS Cluster ARN"
  value       = module.compute.ecs_cluster_arn
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.data.rds_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.data.redis_endpoint
  sensitive   = true
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "ALB Zone ID (for Route53)"
  value       = aws_lb.main.zone_id
}

output "s3_data_bucket" {
  description = "S3 data bucket name"
  value       = module.data.s3_data_us_bucket
}

output "s3_model_artifacts_bucket" {
  description = "S3 model artifacts bucket name"
  value       = module.data.s3_model_artifacts_bucket
}

output "kms_key_arn" {
  description = "KMS key ARN"
  value       = module.security.kms_key_arn
}

output "ecs_task_execution_role_arn" {
  description = "ECS Task Execution Role ARN"
  value       = module.compute.ecs_task_execution_role_arn
}

output "ecs_task_role_arn" {
  description = "ECS Task Role ARN"
  value       = module.compute.ecs_task_role_arn
}

