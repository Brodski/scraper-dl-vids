provider "aws" {
  region = "us-east-1"
}

data "archive_file" "lambda_zip" {
    type = "zip"
    output_path = "${path.module}/output_code.zip"
    source_dir = "${path.module}/auto-vast-runner"
}
resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [ {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }]
  })
}
# Attach the AWSLambdaBasicExecutionRole policy to the role
resource "aws_iam_role_policy_attachment" "lambda_exec_role_attach" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "example_lambda" {
  function_name = "auto-vast-runner"

  filename = data.archive_file.lambda_zip.output_path # "output_code.zip"
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)
  # handler = "test.handler"
  handler = "auto-vast-runner.handler_kickit" 
  runtime = "python3.10"

  role = aws_iam_role.lambda_execution_role.arn
  depends_on = [data.archive_file.lambda_zip]
  environment {
    variables = {
      IS_CREATE_INSTANCE = "true"
      AWS_SECRET_ACCESS_KEY = var.sensitive_configs.AWS_SECRET_ACCESS_KEY
      AWS_ACCESS_KEY_ID = var.sensitive_configs.AWS_ACCESS_KEY_ID
      ENV = var.sensitive_configs.ENV
      DATABASE_HOST = var.sensitive_configs.DATABASE_HOST
      DATABASE_USERNAME = var.sensitive_configs.DATABASE_USERNAME
      DATABASE_PASSWORD = var.sensitive_configs.DATABASE_PASSWORD
      DATABASE = var.sensitive_configs.DATABASE      
    }
  }
}

resource "aws_cloudwatch_event_rule" "daily_event" {
  name                = "run-lambda-daily"
  description         = "Run Lambda function once a day"
  schedule_expression = "cron(0 13 * * ? *)" 
  # schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "daily_lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_event.name
  target_id = "RunDailyLambdaFunction"
  arn       = aws_lambda_function.example_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id   = "AllowExecutionFromCloudWatch"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.example_lambda.function_name
  principal      = "events.amazonaws.com"
  source_arn     = aws_cloudwatch_event_rule.daily_event.arn
}

resource "aws_cloudwatch_log_group" "name" {
    name = "/aws/lambda/${aws_lambda_function.example_lambda.function_name}"
    retention_in_days = 30 # nice 
}

output "path_module" {
  value       = "${path.module}/output_code.zip"
}
output "ouput_lambda_zip" {
  value       = data.archive_file.lambda_zip.output_path
}