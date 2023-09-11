# LAMBDA 
# LAMBDA 
# LAMBDA 
# LAMBDA 
data "archive_file" "lambda_zip" {
    type = "zip"
    output_path = "${path.module}/my_other_lambda.zip"
    source_dir = "${path.module}/"
}

resource "aws_lambda_function" "lambda_fn_test_TWO" {
  function_name = var.lambda_name
  handler       = "app.lambdaHandler2" 
  runtime       = "nodejs16.x"
  # role          = aws_iam_role.lambda_role.arn
  role          = var.iam_lambda_role_arn

  filename = data.archive_file.lambda_zip.output_path #"my_lambda.zip"
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)


  environment {
    variables = {
      FLASK_ENV = "DEV"
    }
  }
}



resource "aws_lambda_permission" "lambda_api" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_fn_test_TWO.function_name
  principal     = "apigateway.amazonaws.com"
  # source_arn = "${aws_api_gateway_deployment.api_gw_deployment.execution_arn}/*/*" 
  source_arn = "${var.api_gateway_deployment_execution_arn}/*/*" 
}

resource "aws_cloudwatch_log_group" "example_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.lambda_fn_test_TWO.function_name}"
  retention_in_days = 14
}
