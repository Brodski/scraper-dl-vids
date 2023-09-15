# LAMBDA 
# LAMBDA 
# LAMBDA 
# LAMBDA 
data "archive_file" "lambda_zip" {
    type = "zip"
    output_path = "${path.module}/../idontfront-app/my_lambda.zip"
    source_dir = "${path.module}/../idontfront-app/"
    # source_dir = "${path.module}/navbar_footer_injector/"
    # source_file = "${path.module}/navbar_footer_injector/app.js"
}

resource "aws_lambda_function" "idontfront_lambda" {
  function_name = var.lambda_name
  handler       = "iDontFront-app.lambdaHandler" 
  runtime       = "nodejs18.x"
  role          = aws_iam_role.lambda_writer_role.arn

  filename = data.archive_file.lambda_zip.output_path #"my_lambda.zip"
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)

  memory_size = 512

  environment {
    variables = {
      FLASK_ENV = "DEV"
      IS_LAMBDA = "true"
    }
  }
}



resource "aws_lambda_permission" "lambda_api" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.idontfront_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_deployment.api_gw_deployment.execution_arn}/*/*" 
}

resource "aws_cloudwatch_log_group" "example_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.idontfront_lambda.function_name}"
  retention_in_days = 14
}

output "ouput_lambda_zip" {
  value       = data.archive_file.lambda_zip.output_path
}
