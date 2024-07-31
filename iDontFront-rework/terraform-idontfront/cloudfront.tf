
locals {
  arn_parts = split(":", aws_api_gateway_rest_api.api_gw_rest.execution_arn)
  region    = local.arn_parts[3]
  api_id    = local.arn_parts[5]
  origin_id = "${var.ENV}-bski-origin-id"
  # origin_id = "bski-captions-id"
}
### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
resource "aws_cloudfront_distribution" "lambda_distribution" {
  enabled = true
  aliases = [local.website_name]
  comment = "${var.ENV}-captions.bski.one"
  viewer_certificate {
    acm_certificate_arn = var.sensitive_info.r53_acm_certificate_arn
    ssl_support_method  = "sni-only"
  }
  origin {
    domain_name = "${local.api_id}.execute-api.${local.region}.amazonaws.com" # 105dijzxb4.execute-api.us-east-1.amazonaws.com
    origin_id   = local.origin_id
    origin_path = "/v1"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }
  # Good condition table: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Expiration.html
  # docs: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-values-specify.html
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.origin_id
    default_ttl = 43200       # 12 hour - applies when origin does not add HTTP headers _
    max_ttl     = 172800      # 48 hours- applies when origin adds headers: Cache-Control max-age, Cache-Control, ect
    min_ttl     = 0           # 0 minute - 0 acts differently then greater than 0. (0 is like a null, does diff things)

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    viewer_protocol_policy = "redirect-to-https"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

# resource "aws_route53_record" "lambda_record" {
#   depends_on = [ aws_cloudfront_distribution.lambda_distribution ]
#   zone_id = var.sensitive_info.r53_route_id
#   name    = local.website_name
#   type    = "A"
#   alias {
#     name                   = aws_cloudfront_distribution.lambda_distribution.domain_name
#     zone_id                = aws_cloudfront_distribution.lambda_distribution.hosted_zone_id
#     evaluate_target_health = false
#   }
# }