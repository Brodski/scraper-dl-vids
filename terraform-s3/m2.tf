# use terraform to satisfy these: 
# build an s3 bucket, this s3 bucket should only be accessible by me and my apps, 
# build a python lambda function from an uploaded zip file, 
# runs this lambda once a week on monday, 
# and only me and the lambda function could access the s3 bucket.
provider "aws" {
  region = "us-west-2"
}

locals {
  account_id = "<your_aws_account_id>"
}

resource "aws_s3_bucket" "example_bucket" {
  bucket = "example-bucket"
  acl    = "private"
}

resource "aws_s3_bucket_policy" "example_bucket_policy" {
  bucket = aws_s3_bucket.example_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${local.account_id}:root"
        }
        Action = "s3:*"
        Resource = [
          aws_s3_bucket.example_bucket.arn,
          "${aws_s3_bucket.example_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Principal = {
          AWS = aws_lambda_function.example_lambda.arn
        }
        Action = "s3:*"
        Resource = [
          aws_s3_bucket.example_bucket.arn,
          "${aws_s3_bucket.example_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_lambda_function" "example_lambda" {
  filename         = "example_lambda-LOCAL.zip"
  function_name = "example-lambda"
  role = aws_iam_role.lambda_role.arn
  handler = "lambda_function.lambda_handler"
  runtime = "python3.8"
  source_code_hash = filebase64sha256("example_lambda-LOCAL.zip")
#   s3_bucket = "<your_upload_bucket>"
#   s3_key = "<path_to_zip>/example_lambda.zip"
    environment {
      variables = {
        S3_BUCKET_NAME = aws_s3_bucket.example_bucket.id
        my_var = "my_valuezz"
        IS_LAMBDA = "true"
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "example_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  policy_arn = aws_iam_policy.s3_access.arn
  role = aws_iam_role.lambda_role.name
}

resource "aws_iam_policy" "s3_access" {
  name = "example_s3_access"
  description = "Allow Lambda to access the S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "s3:*"
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.example_bucket.arn,
          "${aws_s3_bucket.example_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_lambda_event_source_mapping" "example_schedule" {
  event_source_arn = aws_cloudwatch_event_rule.example_schedule.arn
  function_name = aws_lambda_function.example_lambda.arn
}

resource "aws_cloudwatch_event_rule" "example_schedule" {
  name = "example_schedule"
  schedule_expression = "cron(0 12 ? * MON *)"
}

resource "aws_cloudwatch_event_target" "example_target" {
  rule = aws_cloudwatch_event_rule.example_schedule.id
  arn = aws_lambda_function.example_lambda.arn
}

resource "aws_lambda_permission" "example_permission" {
  statement_id = "AllowExecutionFromCloudWatch"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.example_lambda.arn
  principal = "events.amazonaws.com"
  source_arn = aws_cloudwatch_event_rule.example_schedule.arn
}
