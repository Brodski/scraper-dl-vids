resource "aws_cloudwatch_log_group" "name" {
    # name = "/lambda/scraper/${var.sensitive_info.ENV}_transcriber_auto_vast"
    # name = "/lambda/scraper/${local.lambda_name}"
    name = "${local.log_name}"
    retention_in_days = 7
}