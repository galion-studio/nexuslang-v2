# Security Module for GALION.APP Alpha (KMS, Secrets Manager, GuardDuty)

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# KMS Key for data encryption
resource "aws_kms_key" "main" {
  description             = "${var.project_name} encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name        = "${var.project_name}-kms-key"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.project_name}-${var.environment}"
  target_key_id = aws_kms_key.main.key_id
}

# Secrets Manager - Database Password
resource "aws_secretsmanager_secret" "db_password" {
  name        = "${var.project_name}/${var.environment}/db-password"
  description = "Database master password"
  kms_key_id  = aws_kms_key.main.id

  tags = {
    Name        = "${var.project_name}-db-password"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.db_password
}

# Secrets Manager - Redis Auth Token
resource "aws_secretsmanager_secret" "redis_auth_token" {
  name        = "${var.project_name}/${var.environment}/redis-auth-token"
  description = "Redis authentication token"
  kms_key_id  = aws_kms_key.main.id

  tags = {
    Name        = "${var.project_name}-redis-auth-token"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "redis_auth_token" {
  secret_id     = aws_secretsmanager_secret.redis_auth_token.id
  secret_string = var.redis_auth_token
}

# Secrets Manager - JWT Secret
resource "aws_secretsmanager_secret" "jwt_secret" {
  name        = "${var.project_name}/${var.environment}/jwt-secret"
  description = "JWT signing secret"
  kms_key_id  = aws_kms_key.main.id

  tags = {
    Name        = "${var.project_name}-jwt-secret"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id     = aws_secretsmanager_secret.jwt_secret.id
  secret_string = var.jwt_secret
}

# Secrets Manager - API Keys (OpenAI, ElevenLabs, etc.)
resource "aws_secretsmanager_secret" "api_keys" {
  name        = "${var.project_name}/${var.environment}/api-keys"
  description = "External API keys (OpenAI, ElevenLabs, etc.)"
  kms_key_id  = aws_kms_key.main.id

  tags = {
    Name        = "${var.project_name}-api-keys"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id
  secret_string = jsonencode({
    openai_api_key      = var.openai_api_key
    elevenlabs_api_key  = var.elevenlabs_api_key
    openrouter_api_key  = var.openrouter_api_key
  })
}

# GuardDuty (threat detection)
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = false  # Not using EKS in alpha
      }
    }
  }

  tags = {
    Name        = "${var.project_name}-guardduty"
    Environment = var.environment
  }
}

# Security Hub
resource "aws_securityhub_account" "main" {}

resource "aws_securityhub_standards_subscription" "cis" {
  standards_arn = "arn:aws:securityhub:${var.aws_region}::standards/cis-aws-foundations-benchmark/v/1.4.0"
  depends_on    = [aws_securityhub_account.main]
}

# CloudWatch Log Group for security events
resource "aws_cloudwatch_log_group" "security" {
  name              = "/aws/security/${var.project_name}"
  retention_in_days = 90
  kms_key_id        = aws_kms_key.main.arn

  tags = {
    Name        = "${var.project_name}-security-logs"
    Environment = var.environment
  }
}

# SNS Topic for security alerts
resource "aws_sns_topic" "security_alerts" {
  name              = "${var.project_name}-security-alerts"
  kms_master_key_id = aws_kms_key.main.id

  tags = {
    Name        = "${var.project_name}-security-alerts"
    Environment = var.environment
  }
}

resource "aws_sns_topic_subscription" "security_alerts_email" {
  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = var.security_alert_email
}

# CloudWatch Event Rule for GuardDuty findings
resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  name        = "${var.project_name}-guardduty-findings"
  description = "Capture GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
  })

  tags = {
    Name        = "${var.project_name}-guardduty-findings"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "guardduty_to_sns" {
  rule      = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.security_alerts.arn
}

# SNS Topic Policy for CloudWatch Events
resource "aws_sns_topic_policy" "security_alerts" {
  arn = aws_sns_topic.security_alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.security_alerts.arn
      }
    ]
  })
}

