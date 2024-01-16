resource "aws_cloudwatch_log_group" "download_log_group" {
  name = "download_log_group"
  retention_in_days = 30 
}