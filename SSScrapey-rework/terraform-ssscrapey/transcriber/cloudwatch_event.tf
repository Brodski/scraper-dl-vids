resource "aws_cloudwatch_event_rule" "transcriber_schedule" {
  name                = "${var.sensitive_info.ENV}_transcriber_schedule"
  description         = "Run transcriber function once a day"
  schedule_expression = var.transcriber_schedule_cron
}

resource "aws_cloudwatch_event_target" "transcriber_target" {
  rule      = aws_cloudwatch_event_rule.transcriber_schedule.name
  target_id = "RunDailyLambdaFunction"
  arn       = aws_lambda_function.vast_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id   = "AllowExecutionFromCloudWatch"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.vast_lambda.function_name
  principal      = "events.amazonaws.com"
  source_arn     = aws_cloudwatch_event_rule.transcriber_schedule.arn
}
