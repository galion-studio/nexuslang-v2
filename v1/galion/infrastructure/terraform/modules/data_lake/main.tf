# S3 Data Lake with Glue Catalog for GALION.APP

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Glue Catalog Database
resource "aws_glue_catalog_database" "main" {
  name        = "${var.project_name}_data_lake"
  description = "Data lake catalog for ${var.project_name}"

  tags = {
    Name        = "${var.project_name}-data-lake-db"
    Environment = var.environment
  }
}

# Glue Crawler IAM Role
resource "aws_iam_role" "glue_crawler" {
  name = "${var.project_name}-glue-crawler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-glue-crawler-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue_crawler.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_s3_access" {
  name = "${var.project_name}-glue-s3-access"
  role = aws_iam_role.glue_crawler.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.s3_data_bucket_arn,
          "${var.s3_data_bucket_arn}/*"
        ]
      }
    ]
  })
}

# Glue Crawler for Raw Text Data
resource "aws_glue_crawler" "raw_text" {
  database_name = aws_glue_catalog_database.main.name
  name          = "${var.project_name}-raw-text-crawler"
  role          = aws_iam_role.glue_crawler.arn

  s3_target {
    path = "s3://${var.s3_data_bucket_name}/raw/text/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  configuration = jsonencode({
    Version = 1.0
    CrawlerOutput = {
      Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
    }
  })

  tags = {
    Name        = "${var.project_name}-raw-text-crawler"
    Environment = var.environment
  }
}

# Glue Crawler for Raw Audio Data
resource "aws_glue_crawler" "raw_audio" {
  database_name = aws_glue_catalog_database.main.name
  name          = "${var.project_name}-raw-audio-crawler"
  role          = aws_iam_role.glue_crawler.arn

  s3_target {
    path = "s3://${var.s3_data_bucket_name}/raw/audio/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  tags = {
    Name        = "${var.project_name}-raw-audio-crawler"
    Environment = var.environment
  }
}

# Glue Crawler for Raw 3D Data
resource "aws_glue_crawler" "raw_3d" {
  database_name = aws_glue_catalog_database.main.name
  name          = "${var.project_name}-raw-3d-crawler"
  role          = aws_iam_role.glue_crawler.arn

  s3_target {
    path = "s3://${var.s3_data_bucket_name}/raw/3d/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  tags = {
    Name        = "${var.project_name}-raw-3d-crawler"
    Environment = var.environment
  }
}

# Glue Crawler for Gold (processed) Data
resource "aws_glue_crawler" "gold" {
  database_name = aws_glue_catalog_database.main.name
  name          = "${var.project_name}-gold-crawler"
  role          = aws_iam_role.glue_crawler.arn

  s3_target {
    path = "s3://${var.s3_data_bucket_name}/gold/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  tags = {
    Name        = "${var.project_name}-gold-crawler"
    Environment = var.environment
  }
}

# EventBridge Rule to trigger crawler daily
resource "aws_cloudwatch_event_rule" "daily_crawl" {
  name                = "${var.project_name}-daily-crawl"
  description         = "Trigger Glue crawlers daily"
  schedule_expression = "cron(0 2 * * ? *)"  # 2 AM UTC daily

  tags = {
    Name        = "${var.project_name}-daily-crawl"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_event_target" "raw_text_crawler" {
  rule      = aws_cloudwatch_event_rule.daily_crawl.name
  target_id = "RawTextCrawler"
  arn       = aws_glue_crawler.raw_text.arn
  role_arn  = aws_iam_role.eventbridge_glue.arn
}

resource "aws_cloudwatch_event_target" "raw_audio_crawler" {
  rule      = aws_cloudwatch_event_rule.daily_crawl.name
  target_id = "RawAudioCrawler"
  arn       = aws_glue_crawler.raw_audio.arn
  role_arn  = aws_iam_role.eventbridge_glue.arn
}

resource "aws_cloudwatch_event_target" "raw_3d_crawler" {
  rule      = aws_cloudwatch_event_rule.daily_crawl.name
  target_id = "Raw3DCrawler"
  arn       = aws_glue_crawler.raw_3d.arn
  role_arn  = aws_iam_role.eventbridge_glue.arn
}

resource "aws_cloudwatch_event_target" "gold_crawler" {
  rule      = aws_cloudwatch_event_rule.daily_crawl.name
  target_id = "GoldCrawler"
  arn       = aws_glue_crawler.gold.arn
  role_arn  = aws_iam_role.eventbridge_glue.arn
}

# IAM Role for EventBridge to trigger Glue
resource "aws_iam_role" "eventbridge_glue" {
  name = "${var.project_name}-eventbridge-glue-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-eventbridge-glue-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "eventbridge_glue" {
  name = "${var.project_name}-eventbridge-glue-policy"
  role = aws_iam_role.eventbridge_glue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:StartCrawler"
        ]
        Resource = "*"
      }
    ]
  })
}

# Athena Workgroup for querying data lake
resource "aws_athena_workgroup" "main" {
  name = "${var.project_name}-workgroup"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${var.s3_data_bucket_name}/athena-results/"

      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key           = var.kms_key_arn
      }
    }
  }

  tags = {
    Name        = "${var.project_name}-athena-workgroup"
    Environment = var.environment
  }
}

