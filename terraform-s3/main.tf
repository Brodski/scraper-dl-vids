# gpt 4
# use terraform to build an s3 bucket, this s3 bucket should only be 
# accessible by me and my apps, and a lambda function that runs once a 
# week and only me and the lambda function could access the s3 bucket

provider "aws" {
  region = "us-west-2"
}

locals {
  lambda_schedule_expression = "rate(1 week)"
}

resource "aws_s3_bucket" "this" {
  bucket = "my-unique-bucket-name"
  acl    = "private"
}

# Q: create an s3 bucket with the folders "channels/raw" and "channels/scrapped"
resource "aws_s3_bucket_object" "channels_raw" {
  bucket       = aws_s3_bucket.this.id
  key          = "channels/raw/"
  content_type = "application/x-directory"
  source       = "/dev/null" # placeholder b/c required. since not uploading actual content use /dev/null
}

resource "aws_s3_bucket_object" "channels_scrapped" {
  bucket       = aws_s3_bucket.this.id
  key          = "channels/scrapped/"
  content_type = "application/x-directory"
  source       = "/dev/null"
}

resource "aws_iam_role" "lambda_role" {
  name = "my_lambda_role"

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

resource "aws_iam_role_policy" "lambda_policy" {
  name = "my_lambda_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = ["${aws_s3_bucket.this.arn}", "${aws_s3_bucket.this.arn}/*"]
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "my_lambda_function" {
  filename      = "lambda_function.zip"
  function_name = "my_lambda_function"
  role          = aws_iam_role.lambda_function.arn
  handler       = "lambda_function.handler"
  runtime       = "python3.9"

  source_code_hash = filebase64sha256("lambda_function.zip")

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.my_bucket.id
    }
  }
}

resource "aws_cloudwatch_event_rule" "weekly_schedule" {
  name        = "weekly_lambda_schedule"
  description = "Trigger the Lambda function once a week"
  schedule_expression = local.lambda_schedule_expression
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.weekly_schedule.name
  target_id = "my_lambda_target"
  arn       = aws_lambda_function.this.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_schedule.arn
}
