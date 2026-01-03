locals {
  lambda_name = "${var.sensitive_info.ENV}_vastai_master"
  log_name = "/lambda/vastai_master/${var.sensitive_info.ENV}"
}

resource "null_resource" "build_app" {
  provisioner "local-exec" {
    # command     = "build.ps1"
    command     = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File build.ps1"
    working_dir = "${path.module}/../../src_vastai_master"
  }
  triggers = {
    always = timestamp()
  }
}

data "archive_file" "lambda_zip" {
    depends_on = [
      null_resource.build_app
    ]
    type = "zip"
    output_path = "${path.module}/../../src_vastai_master/output_vastai_lambda_code.zip"
    source_dir = "${path.module}/../../src_vastai_master/build"
}

resource "aws_lambda_function" "vast_lambda" {
  function_name = "${local.lambda_name}"

  filename = data.archive_file.lambda_zip.output_path # "output_vastai_lambda_code.zip"
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)
  handler = "vastai_master.handler_kickit" 
  runtime = "python3.10"
  timeout = 900 # 15 minutes

  role = aws_iam_role.lambda_execution_role.arn

  logging_config {
    log_format = "Text"
    log_group = local.log_name
  }

  environment {
    variables = {
      IS_VASTAI_CREATE_INSTANCE     = var.IS_VASTAI_CREATE_INSTANCE
      VAST_API_KEY                  = var.sensitive_info.VAST_API_KEY
      MY_AWS_SECRET_ACCESS_KEY      = var.sensitive_info.MY_AWS_SECRET_ACCESS_KEY
      MY_AWS_ACCESS_KEY_ID          = var.sensitive_info.MY_AWS_ACCESS_KEY_ID
      ENV                           = var.sensitive_info.ENV
      DATABASE_HOST                 = var.sensitive_info.DATABASE_HOST
      DATABASE_USERNAME             = var.sensitive_info.DATABASE_USERNAME
      DATABASE_PASSWORD             = var.sensitive_info.DATABASE_PASSWORD
      DATABASE_PORT                 = var.sensitive_info.DATABASE_PORT
      DATABASE                      = var.sensitive_info.DATABASE
      DOCKER                        = var.docker_image
      TRANSCRIBER_NUM_INSTANCES     = var.transcriber_num_instances
      TRANSCRIBER_VODS_PER_INSTANCE = var.transcriber_vods_per_instance
      TRANSCRIBER_MODEL_SIZE_OVERRIDE  = var.transcriber_model_size_override
    }
  }
}
