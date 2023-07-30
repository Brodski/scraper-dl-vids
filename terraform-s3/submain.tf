# make me a terraform file that will make a aws lambda function, 
# this lambda function should upload a python flask app from a local 
# zip file, and then make me a cloudfront distribution that will cache 
# this lambda function.
# gpt4
provider "aws" {
  region = "us-west-2"
}

locals {
  lambda_function_name = "flask_app_lambda"
}

resource "aws_lambda_function" "flask_app" {
  function_name = local.lambda_function_name
  handler       = "app.lambda_handler" # Change to your handler location
  runtime       = "python3.8"
  role          = aws_iam_role.lambda_exec.arn
  filename      = "flask_app.zip" # Your local ZIP file

  environment {
    variables = {
      FLASK_APP = "app.py"
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec"

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

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_exec.name
}

resource "aws_lambda_permission" "allow_cloudfront" {
  statement_id  = "AllowCloudFront"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.flask_app.function_name
  principal     = "cloudfront.amazonaws.com"
  source_arn    = aws_cloudfront_distribution.distribution.arn
}

resource "aws_cloudfront_distribution" "distribution" {
  origin {
    domain_name = aws_lambda_function.flask_app.arn
    origin_id   = "Lambda"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "Lambda"

    forwarded_values {
      query_string = false
      headers      = ["Origin"]

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600 # 1 hour cache
    max_ttl                = 86400
    compress               = true

    lambda_function_association {
      event_type   = "origin-request"
      lambda_arn   = aws_lambda_function.flask_app.qualified_arn
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

#   viewer_certificate {
#     cloudfront_default_certificate = true
#   }
# In my cloudfront distribution, I have a Custom SSL certificate of my own, how could I  use that?
    viewer_certificate {
    acm_certificate_arn      = "<your_acm_certificate_arn>"
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2018"
    }
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.distribution.domain_name
}