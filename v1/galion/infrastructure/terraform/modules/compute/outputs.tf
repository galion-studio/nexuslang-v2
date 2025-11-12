# Outputs for Compute Module

output "ecs_cluster_id" {
  description = "ECS Cluster ID"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_name" {
  description = "ECS Cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ECS Cluster ARN"
  value       = aws_ecs_cluster.main.arn
}

output "ecs_task_execution_role_arn" {
  description = "ECS Task Execution Role ARN"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ECS Task Role ARN"
  value       = aws_iam_role.ecs_task.arn
}

output "general_asg_name" {
  description = "General Auto Scaling Group name"
  value       = aws_autoscaling_group.general.name
}

output "gpu_asg_name" {
  description = "GPU Auto Scaling Group name"
  value       = aws_autoscaling_group.gpu.name
}

output "general_capacity_provider_name" {
  description = "General Capacity Provider name"
  value       = aws_ecs_capacity_provider.general.name
}

output "gpu_capacity_provider_name" {
  description = "GPU Capacity Provider name"
  value       = aws_ecs_capacity_provider.gpu.name
}

