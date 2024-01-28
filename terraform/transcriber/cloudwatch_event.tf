resource "aws_cloudwatch_event_rule" "transcriber_schedule" {
  name                = "transcriber_schedule"
  description         = "Run transcriber function once a day"
  schedule_expression = "cron(0 9 * * ? *)" 
  # schedule_expression = "rate(1 minute)"
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
