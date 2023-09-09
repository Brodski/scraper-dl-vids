variable "VAST_API_KEY" {
  description = "Secret API Key"
  type        = string
  sensitive   = true
  default     = "x" 
  # terraform apply -var "api_key=1234567890"
  # OR
  # export TF_VAR_api_key="your_actual_api_key_here" --- LINUX
  # $env:TF_VAR_api_key = "your_actual_api_key_here" --- WINDOWS
  # OR
  # load 'api_key' from the .env file
}
variable "MY_AWS_SECRET_ACCESS_KEY" {
  description = "Secret AWS Access Key"
  type        = string
  sensitive   = true
  default     = "XX" 
}
variable "MY_AWS_ACCESS_KEY_ID" {
  description = "AWS Access ID"
  type        = string
  sensitive   = true
  default     = "XXX" 
}

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
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
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
      MY_VARIABLE     = "MyValue"
      VAST_API_KEY    = var.VAST_API_KEY
      IS_CREATE_INSTANCE = "true"
      MY_AWS_SECRET_ACCESS_KEY = var.MY_AWS_SECRET_ACCESS_KEY
      MY_AWS_ACCESS_KEY_ID = var.MY_AWS_ACCESS_KEY_ID
    }
  }
}

resource "aws_cloudwatch_event_rule" "daily_event" {
  name                = "run-lambda-daily"
  description         = "Run Lambda function once a day"
  schedule_expression = "cron(0 13 * * ? *)" # 12 = ECS
  # schedule_expression = "cron(30 12 * * ? *)" # daily at 11:00am UTC
  # schedule_expression = "cron(0 * * * ? *)" # Every minute
  # schedule_expression = "rate(1 minute)"
  # schedule_expression = "rate(1 hour)"
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