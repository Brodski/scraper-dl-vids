# LAMBDA 
# LAMBDA 
# LAMBDA 
# LAMBDA 
locals {
  shit =  "${path.module}/Archive.zip"
}

data "archive_file" "lambda_zip" {
    type = "zip"
    output_path = "${path.module}/my_lambda.zip"
    source_dir = "${path.module}/../idontfront-app/"
    # source_dir = "${path.module}/navbar_footer_injector/"
    # source_file = "${path.module}/navbar_footer_injector/app.js"
}

resource "aws_lambda_function" "idontfront_lambda" {
  depends_on = [ aws_s3_bucket_object.lambda_code ]
  function_name = var.lambda_name
  handler       = "iDontFront-app.lambdaHandler" 
  runtime       = "nodejs18.x"
  role          = aws_iam_role.lambda_writer_role.arn

  # filename = data.archive_file.lambda_zip.output_path #"my_lambda.zip"
  # source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)
  source_code_hash = filebase64sha256(local.shit)

  memory_size = 512
  timeout = 15 
  architectures    = ["x86_64"]
  # architectures    = ["arm64"]

  s3_bucket        = "idontfront-lambda-zips"
  s3_key           = "my_lambda.zip"

  environment {
    variables = {
      FLASK_ENV = "DEV"
      IS_LAMBDA = "true"
      # LD_PRELOAD = "/var/task/node_modules/canvas/build/Release/libz.so.1"
      # LDFLAGS="-Wl",-rpath=/var/task/lib"
    }
  }
}

resource "aws_s3_bucket_object" "lambda_code" {
  # bucket = aws_s3_bucket.lambda_bucket.bucket
  bucket = "idontfront-lambda-zips"
  key    = "my_lambda.zip"
  # source = data.archive_file.lambda_zip.output_path
  # etag   = filemd5(data.archive_file.lambda_zip.output_path)
  source = local.shit
  etag   = filemd5(local.shit)
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
  # value       = data.archive_file.lambda_zip.output_path
  value       = local.shit
}
