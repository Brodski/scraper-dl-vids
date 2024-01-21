data "archive_file" "lambda_zip" {
    type = "zip"
    output_path = "${path.module}/output_code.zip"
    source_dir = "${path.module}/auto-vast-runner"
}

resource "aws_lambda_function" "vast_lambda" {
  function_name = "auto-vast-runner"

  filename = data.archive_file.lambda_zip.output_path # "output_code.zip"
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)
  handler = "auto-vast-runner.handler_kickit" 
  runtime = "python3.10"

  role = aws_iam_role.lambda_execution_role.arn
  depends_on = [data.archive_file.lambda_zip]
  environment {
    variables = {
      IS_VASTAI_CREATE_INSTANCE = var.IS_VASTAI_CREATE_INSTANCE
      AWS_SECRET_ACCESS_KEY = var.sensitive_info.AWS_SECRET_ACCESS_KEY
      AWS_ACCESS_KEY_ID = var.sensitive_info.AWS_ACCESS_KEY_ID
      ENV = var.sensitive_info.ENV
      DATABASE_HOST = var.sensitive_info.DATABASE_HOST
      DATABASE_USERNAME = var.sensitive_info.DATABASE_USERNAME
      DATABASE_PASSWORD = var.sensitive_info.DATABASE_PASSWORD
      DATABASE = var.sensitive_info.DATABASE      
      DOCKER = var.docker_image
    }
  }
}
