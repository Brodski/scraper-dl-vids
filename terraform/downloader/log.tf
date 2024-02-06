resource "aws_cloudwatch_log_group" "download_log_group" {
  name = "/scraper/downloader_${var.sensitive_info.ENV}"
  retention_in_days = 3
}