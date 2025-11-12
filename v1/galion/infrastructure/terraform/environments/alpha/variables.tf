# Variables for Alpha Environment

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "galion-app"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "alpha"
}

# Networking
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

# Compute
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

# Database
variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.medium"
}

variable "rds_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "galionapp"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "galionadmin"
}

variable "db_password" {
  description = "Database master password (store in terraform.tfvars, not in git)"
  type        = string
  sensitive   = true
}

# Redis
variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.t4g.small"
}

variable "redis_auth_token" {
  description = "Redis auth token (store in terraform.tfvars, not in git)"
  type        = string
  sensitive   = true
}

# Security
variable "jwt_secret" {
  description = "JWT signing secret (store in terraform.tfvars, not in git)"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key (optional for alpha)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "elevenlabs_api_key" {
  description = "ElevenLabs API key (optional for alpha)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "openrouter_api_key" {
  description = "OpenRouter API key (optional for alpha)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "security_alert_email" {
  description = "Email address for security alerts"
  type        = string
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS (create manually in AWS Console)"
  type        = string
}

