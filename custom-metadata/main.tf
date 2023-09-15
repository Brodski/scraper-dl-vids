provider "aws" {
  region = "us-east-1"
}
data "archive_file" "lambda_zip" {
    type = "zip"
    output_path = "${path.module}/output.zip"
    # source_dir = "${path.module}/"
    source_file = "${path.module}/custom-metadata-app.py"
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_writer_role" {
  name = "lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Effect = "Allow",
        Sid = ""
      }
    ]
  })
}

# AWS Lambda function
resource "aws_lambda_function" "flask_lambda" {
  function_name    = "flask_lambda"
  handler          = "app.lambda_handler" # Change to your handler location in the ZIP file
  runtime          = "python3.10"
  role             = aws_iam_role.lambda_writer_role.arn
  filename         = "output.zip" # Your local ZIP file containing the Flask app

  source_code_hash = filebase64sha256("output.zip")

  environment {
    variables = {
      FLASK_ENV = "production"
      IS_LAMBDA = "true"
    }
  }
}


# API Gateway configuration
resource "aws_api_gateway_rest_api" "flask_api" {
  name        = "flask_api"
  description = "API for Flask App"
}

resource "aws_api_gateway_resource" "flask_resource" {
  rest_api_id = aws_api_gateway_rest_api.flask_api.id
  parent_id   = aws_api_gateway_rest_api.flask_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.flask_api.id
  resource_id   = aws_api_gateway_resource.flask_resource.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.flask_api.id
  resource_id = aws_api_gateway_resource.flask_resource.id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.flask_lambda.invoke_arn
}

resource "aws_api_gateway_deployment" "flask_deployment" {
  depends_on = [aws_api_gateway_integration.lambda]

  rest_api_id = aws_api_gateway_rest_api.flask_api.id
  stage_name  = "prod"
}

output "api_url" {
  value = aws_api_gateway_deployment.flask_deployment.invoke_url
}

output "path_module" {
  value = "${path.module}/output.zip"
}
