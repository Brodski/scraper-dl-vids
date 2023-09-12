### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
resource "aws_cloudfront_distribution" "lambda_distribution" {
  enabled = true
  aliases = [var.r53_lambda_full_domain]
  viewer_certificate {
    acm_certificate_arn = var.r53_acm_certificate_arn
    ssl_support_method  = "sni-only"
  }
  origin {
    domain_name = "${local.api_id}.execute-api.${local.region}.amazonaws.com" # 105dijzxb4.execute-api.us-east-1.amazonaws.com
    origin_id   = "exampleOriginId"
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
    target_origin_id = "exampleOriginId"
    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
    viewer_protocol_policy = "allow-all" #One of allow-all, https-only, or redirect-to-https.
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
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