locals {
  lambda_env_name = "${var.ENV}_${var.lambda_name}"
  log_name        = "/scraper/mini_image/${var.ENV}"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir = "${path.module}/../mini-image-app"
  output_path = "${path.module}/../lambda_function_payload.zip"
}


resource "aws_lambda_function" "mini_image_lambda" {
  depends_on = [data.archive_file.lambda_zip]
  function_name = local.lambda_env_name
  role          = aws_iam_role.mini_image_role.arn
  memory_size   = 512
  timeout       = 300 # 5 min 
  architectures = ["arm64"] # ["x86_64"] # 


  filename = data.archive_file.lambda_zip.output_path # "output_code.zip"
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)
  # source_code_hash = data.archive_file.lambda.output_base64sha256
  handler = "app-mini-image.lambdaHandler" 
  runtime = "nodejs18.x"

  logging_config {
    log_format = "Text"
    log_group = local.log_name
  }

  environment {
    variables = {
      FLASK_ENV = var.ENV
      IS_LAMBDA = "true"
      ENV = var.ENV
    }
  }
}

resource "aws_lambda_permission" "lambda_api" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mini_image_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api_gw_rest.execution_arn}/*/*" 
  # source_arn = "${aws_api_gateway_deployment.api_gw_deployment.execution_arn}/*/*" 
}

resource "aws_cloudwatch_log_group" "logs" {
  name              = local.log_name
  retention_in_days = 30
}
