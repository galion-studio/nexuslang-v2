# Variables for Compute Module

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (alpha, beta, prod)"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for ECS instances"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "Security group ID for ECS tasks"
  type        = string
}

variable "ecs_ami_id" {
  description = "AMI ID for ECS-optimized instances"
  type        = string
  default     = ""  # Will use latest ECS-optimized AMI if not specified
}

variable "ecs_gpu_ami_id" {
  description = "AMI ID for ECS GPU-optimized instances"
  type        = string
  default     = ""  # Will use latest ECS GPU-optimized AMI if not specified
}

variable "general_instance_type" {
  description = "Instance type for general workloads"
  type        = string
  default     = "m7i.large"
}

variable "gpu_instance_type" {
  description = "Instance type for GPU workloads"
  type        = string
  default     = "g5.2xlarge"
}

variable "general_min_size" {
  description = "Minimum number of general instances"
  type        = number
  default     = 2
}

variable "general_max_size" {
  description = "Maximum number of general instances"
  type        = number
  default     = 4
}

variable "general_desired_capacity" {
  description = "Desired number of general instances"
  type        = number
  default     = 2
}

variable "gpu_min_size" {
  description = "Minimum number of GPU instances"
  type        = number
  default     = 1
}

variable "gpu_max_size" {
  description = "Maximum number of GPU instances"
  type        = number
  default     = 2
}

variable "gpu_desired_capacity" {
  description = "Desired number of GPU instances"
  type        = number
  default     = 1
}

