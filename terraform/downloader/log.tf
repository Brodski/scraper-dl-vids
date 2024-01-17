resource "aws_cloudwatch_log_group" "download_log_group" {
  name = "/ecs/scraper/${var.sensitive_info.ENV}_downloader"
  retention_in_days = 30 
}