resource "aws_cloudwatch_log_group" "preper_log_group" {
  name = "/scraper/preper_${var.sensitive_info.ENV}"
  retention_in_days = 30 
}