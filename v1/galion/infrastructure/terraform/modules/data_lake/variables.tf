# Variables for Data Lake Module

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (alpha, beta, prod)"
  type        = string
}

variable "s3_data_bucket_name" {
  description = "S3 data bucket name"
  type        = string
}

variable "s3_data_bucket_arn" {
  description = "S3 data bucket ARN"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS key ARN for encryption"
  type        = string
}

