locals {
  lambda_env_name = "${var.ENV}_${var.lambda_name}"
  log_name        = "/website/idontfront/${var.ENV}"
  image_uri       = "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:${var.docker_tag_name}"
}
resource "aws_lambda_function" "idontfront_lambda" {
  function_name = local.lambda_env_name
  role          = aws_iam_role.idont_writer_role.arn
  memory_size   = 512
  timeout       = 600 # 10 min 
  architectures = ["x86_64"] # ["arm64"]

  ### Deploy: Docker Container
  package_type = "Image"
  image_uri = local.image_uri

  logging_config {
    log_format = "Text"
    log_group = local.log_name
  }

  environment {
    variables = {
      FLASK_ENV = var.ENV
      IS_LAMBDA = "true"
      ENV = var.ENV
      DATABASE_HOST = var.sensitive_info.DATABASE_HOST 
      DATABASE_USERNAME = var.sensitive_info.DATABASE_USERNAME 
      DATABASE_PASSWORD = var.sensitive_info.DATABASE_PASSWORD 
      DATABASE = var.sensitive_info.DATABASE 
      BUCKET_DOMAIN = var.sensitive_info.BUCKET_DOMAIN
      # BUCKET_DOMAIN=https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com

      # LD_PRELOAD = "/var/task/node_modules/canvas/build/Release/libz.so.1"
      # LDFLAGS="-Wl",-rpath=/var/task/lib"
    }
  }
}

resource "aws_lambda_permission" "lambda_api" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.idontfront_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api_gw_rest.execution_arn}/*/*" 
  # source_arn = "${aws_api_gateway_deployment.api_gw_deployment.execution_arn}/*/*" 
}

resource "aws_cloudwatch_log_group" "logs" {
  name              = local.log_name
  # name              = "/scraper/idontfront/${var.ENV}_${var.lambda_name}"
  retention_in_days = 14
}
