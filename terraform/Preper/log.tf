resource "aws_cloudwatch_log_group" "preper_log_group" {
  name = "preper_log_group"
  retention_in_days = 30 
}