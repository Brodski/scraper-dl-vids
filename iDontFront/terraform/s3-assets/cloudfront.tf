# CLOUDFRONT S3 ASSETS
# CLOUDFRONT S3 ASSETS
# CLOUDFRONT S3 ASSETS
# CLOUDFRONT S3 ASSETS
# CLOUDFRONT S3 ASSETS
resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name = aws_s3_bucket.s3_test_assets_bucket.bucket_regional_domain_name
    origin_id   = aws_s3_bucket.s3_test_assets_bucket.id
  }
  enabled             = true
  comment             = "CloudFront Distribution for S3 Bucket"
  aliases             = [var.r53_s3_asset_full_domain]
  default_root_object = "hulk.webp"
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = aws_s3_bucket.s3_test_assets_bucket.id
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }
  # logging_config {
  #   include_cookies = false
  #   bucket          = "${aws_s3_bucket.log_bucket.bucket_domain_name}"
  #   prefix          = "cf-s3-dist-logs/"
  # }

  viewer_certificate {
    acm_certificate_arn = var.r53_acm_certificate_arn
    ssl_support_method  = "sni-only"
    minimum_protocol_version = "TLSv1.2_2018"
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  tags = {
    Name = "s3_distribution"
  }
}
