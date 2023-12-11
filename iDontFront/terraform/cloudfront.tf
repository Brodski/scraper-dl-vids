
locals {
  arn_parts = split(":", aws_api_gateway_rest_api.api_gw_rest.execution_arn)
  region    = local.arn_parts[3]
  api_id    = local.arn_parts[5]
}
### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
resource "aws_cloudfront_distribution" "lambda_distribution" {
  enabled = true
  aliases = [var.r53_lambda_full_domain]
  comment = "bski cc cloudfront"
  viewer_certificate {
    acm_certificate_arn = var.r53_acm_certificate_arn
    ssl_support_method  = "sni-only"
  }
  origin {
    domain_name = "${local.api_id}.execute-api.${local.region}.amazonaws.com" # 105dijzxb4.execute-api.us-east-1.amazonaws.com
    origin_id   = "bski-captions-id"
    origin_path = "/v1"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "bski-captions-id"

    default_ttl = 43200       # Default TTL set to 12 hour
    max_ttl     = 172800      # Max TTL set to 48 hours
    min_ttl     = 0           # Min TTL set to 0 minute
    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
    viewer_protocol_policy = "redirect-to-https"
    # viewer_protocol_policy = "allow-all" #One of allow-all, https-only, or redirect-to-https.
  }
  # logging_config {
  #   include_cookies = false
  #   bucket          = "${aws_s3_bucket.log_bucket.bucket_domain_name}"
  #   prefix          = "cf-lambda-dist-logs/"
  # }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}