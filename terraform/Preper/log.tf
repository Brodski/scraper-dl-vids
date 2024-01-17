resource "aws_cloudwatch_log_group" "preper_log_group" {
  name = "/ecs/scraper/${var.sensitive_info.ENV}_preper"
  retention_in_days = 30 
}