resource "aws_cloudwatch_log_group" "name" {
    name = "/aws/lambda/${aws_lambda_function.example_lambda.function_name}"
    retention_in_days = 30
}