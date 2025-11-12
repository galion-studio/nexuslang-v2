# GALION.APP Alpha Environment Configuration

terraform {
  required_version = ">= 1.6.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "galion-terraform-state"  # Create this bucket manually first
    key            = "alpha/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "galion-terraform-locks"  # Create this table manually first
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "galion-app"
      Environment = "alpha"
      ManagedBy   = "terraform"
    }
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Data source for ECS-optimized AMI
data "aws_ami" "ecs_optimized" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }
}

# Data source for ECS GPU-optimized AMI
data "aws_ami" "ecs_gpu_optimized" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-gpu-hvm-*-x86_64-ebs"]
  }
}

# Security Module (KMS, Secrets Manager, GuardDuty)
module "security" {
  source = "../../modules/security"

  project_name          = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  db_password           = var.db_password
  redis_auth_token      = var.redis_auth_token
  jwt_secret            = var.jwt_secret
  openai_api_key        = var.openai_api_key
  elevenlabs_api_key    = var.elevenlabs_api_key
  openrouter_api_key    = var.openrouter_api_key
  security_alert_email  = var.security_alert_email
}

# Networking Module (VPC, Subnets, Security Groups)
module "networking" {
  source = "../../modules/networking"

  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  availability_zones   = slice(data.aws_availability_zones.available.names, 0, 2)
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

# Data Module (RDS, Redis, S3)
module "data" {
  source = "../../modules/data"

  project_name            = var.project_name
  environment             = var.environment
  private_subnet_ids      = module.networking.private_subnet_ids
  rds_security_group_id   = module.networking.rds_security_group_id
  redis_security_group_id = module.networking.redis_security_group_id
  kms_key_arn             = module.security.kms_key_arn
  rds_instance_class      = var.rds_instance_class
  rds_allocated_storage   = var.rds_allocated_storage
  db_name                 = var.db_name
  db_username             = var.db_username
  db_password             = var.db_password
  redis_node_type         = var.redis_node_type
  redis_auth_token        = var.redis_auth_token
}

# Compute Module (ECS, EC2, Auto Scaling)
module "compute" {
  source = "../../modules/compute"

  project_name            = var.project_name
  environment             = var.environment
  private_subnet_ids      = module.networking.private_subnet_ids
  ecs_security_group_id   = module.networking.ecs_tasks_security_group_id
  ecs_ami_id              = data.aws_ami.ecs_optimized.id
  ecs_gpu_ami_id          = data.aws_ami.ecs_gpu_optimized.id
  general_instance_type   = var.general_instance_type
  gpu_instance_type       = var.gpu_instance_type
  general_min_size        = var.general_min_size
  general_max_size        = var.general_max_size
  general_desired_capacity = var.general_desired_capacity
  gpu_min_size            = var.gpu_min_size
  gpu_max_size            = var.gpu_max_size
  gpu_desired_capacity    = var.gpu_desired_capacity

  depends_on = [module.networking]
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [module.networking.alb_security_group_id]
  subnets            = module.networking.public_subnet_ids

  enable_deletion_protection = false
  enable_http2               = true
  enable_cross_zone_load_balancing = true

  tags = {
    Name        = "${var.project_name}-alb"
    Environment = var.environment
  }
}

# ALB Target Group for API Gateway
resource "aws_lb_target_group" "api_gateway" {
  name        = "${var.project_name}-api-gateway-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = module.networking.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = {
    Name        = "${var.project_name}-api-gateway-tg"
    Environment = var.environment
  }
}

# ALB Listener (HTTPS)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_gateway.arn
  }
}

# ALB Listener (HTTP - redirect to HTTPS)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# CloudWatch Log Groups for ECS services
resource "aws_cloudwatch_log_group" "ecs_services" {
  for_each = toset(["api-gateway", "auth-service", "user-service", "voice-service"])

  name              = "/ecs/${var.project_name}/${each.key}"
  retention_in_days = 30
  kms_key_id        = module.security.kms_key_arn

  tags = {
    Name        = "${var.project_name}-${each.key}-logs"
    Environment = var.environment
  }
}

