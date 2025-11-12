# Outputs for Data Module

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_address" {
  description = "RDS address"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "RDS port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.postgres.db_name
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "redis_port" {
  description = "Redis port"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].port
}

output "s3_data_us_bucket" {
  description = "S3 bucket name for US data"
  value       = aws_s3_bucket.data_us.id
}

output "s3_data_us_arn" {
  description = "S3 bucket ARN for US data"
  value       = aws_s3_bucket.data_us.arn
}

output "s3_model_artifacts_bucket" {
  description = "S3 bucket name for model artifacts"
  value       = aws_s3_bucket.model_artifacts.id
}

output "s3_model_artifacts_arn" {
  description = "S3 bucket ARN for model artifacts"
  value       = aws_s3_bucket.model_artifacts.arn
}

output "s3_static_bucket" {
  description = "S3 bucket name for static assets"
  value       = aws_s3_bucket.static.id
}

output "s3_static_arn" {
  description = "S3 bucket ARN for static assets"
  value       = aws_s3_bucket.static.arn
}

output "s3_logs_bucket" {
  description = "S3 bucket name for logs"
  value       = aws_s3_bucket.logs.id
}

output "s3_logs_arn" {
  description = "S3 bucket ARN for logs"
  value       = aws_s3_bucket.logs.arn
}

