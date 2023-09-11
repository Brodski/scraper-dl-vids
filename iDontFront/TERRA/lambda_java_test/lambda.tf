resource "aws_lambda_function" "lambda_java_fn" {
  function_name = var.lambda_name
  handler       = "helloworld.App::handleRequest"
  runtime       = "java11"
  role          = var.iam_lambda_role_arn
  architectures = ["arm64"]
  timeout = 20
  memory_size = 512
  filename = "lambda_java_test/HelloWorldFunction/target/HelloWorld-1.0.jar"
  source_code_hash = filebase64sha256("lambda_java_test/HelloWorldFunction/target/HelloWorld-1.0.jar")
  environment {
    variables = {
      FLASK_ENV = "DEVVVVVV"
    }
  }
}

resource "aws_lambda_permission" "lambda_api_java" {
  # statement_id  = "AllowExecutionFromAPIGateway"
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_java_fn.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${var.api_gateway_deployment_execution_arn}/*/*" 
}

resource "aws_cloudwatch_log_group" "example_lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.lambda_java_fn.function_name}"
  retention_in_days = 14
}

output "SOURCE_ARN_PERMISSION" {
  value = aws_lambda_permission.lambda_api_java.source_arn  
}
