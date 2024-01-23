resource "aws_cloudwatch_event_rule" "daily_event" {
  name                = "run-lambda-daily"
  description         = "Run Lambda function once a day"
  schedule_expression = "cron(43 8 * * ? *)" 
  # schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "daily_lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_event.name
  target_id = "RunDailyLambdaFunction"
  arn       = aws_lambda_function.vast_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id   = "AllowExecutionFromCloudWatch"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.vast_lambda.function_name
  principal      = "events.amazonaws.com"
  source_arn     = aws_cloudwatch_event_rule.daily_event.arn
}
