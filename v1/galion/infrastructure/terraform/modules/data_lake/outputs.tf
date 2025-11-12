# Outputs for Data Lake Module

output "glue_database_name" {
  description = "Glue catalog database name"
  value       = aws_glue_catalog_database.main.name
}

output "glue_crawler_raw_text_name" {
  description = "Glue crawler name for raw text data"
  value       = aws_glue_crawler.raw_text.name
}

output "glue_crawler_raw_audio_name" {
  description = "Glue crawler name for raw audio data"
  value       = aws_glue_crawler.raw_audio.name
}

output "glue_crawler_raw_3d_name" {
  description = "Glue crawler name for raw 3D data"
  value       = aws_glue_crawler.raw_3d.name
}

output "glue_crawler_gold_name" {
  description = "Glue crawler name for gold data"
  value       = aws_glue_crawler.gold.name
}

output "athena_workgroup_name" {
  description = "Athena workgroup name"
  value       = aws_athena_workgroup.main.name
}

