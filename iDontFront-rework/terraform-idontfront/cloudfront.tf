
locals {
  arn_parts = split(":", aws_api_gateway_rest_api.api_gw_rest.execution_arn)
  region    = local.arn_parts[3]
  api_id    = local.arn_parts[5]
  origin_id = "${var.ENV}-bski-origin-id"
  cache_long = ( var.ENV == "dev"  ? 300 :                     # 5 minutes
                 var.ENV == "prod" ? 86400 : "default_value" ) # 1 days
}

### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
### CLOUDFRONT LAMBDA
resource "aws_cloudfront_distribution" "lambda_distribution" {
  enabled = true
  aliases = local.website_name
  comment = join(", ", local.website_name)
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
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = local.origin_id

    default_ttl = local.cache_long     # 1 days - applies when origin does not add HTTP headers _
    max_ttl     = local.cache_long     # 1 days - applies when origin adds headers: Cache-Control max-age, Cache-Control, ect
    min_ttl     = 0                    # 0 minute - 0 acts differently then greater than 0. (0 is like a null, does diff things)

    compress = true # compress when header: `Accept-Encoding: gzip`

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.url_rewrite_function.arn
    }
    forwarded_values { 
      # headers that are forwarded: Host, X-Amz-Cf-Id, X-Forwarded-For, User-Agent, and Via
      query_string = false
      cookies {
        forward = "none" 
      }
    }
    viewer_protocol_policy = "redirect-to-https"
  }

  custom_error_response {
    error_code            = 404
    error_caching_min_ttl = 300  # Cache the 400 response for 5 minutes
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

resource "aws_cloudfront_function" "url_rewrite_function" {
  name    = "url-rewrite-function-${var.ENV}"
  runtime = "cloudfront-js-2.0"
  comment = "www rewrite"
  publish = true

  # https://github.com/aws-samples/amazon-cloudfront-functions/blob/main/redirect-based-on-country/index.js
  code = <<EOF
function handler(event) {
    var request = event.request;
    var host = request.headers.host ? request.headers.host.value : null;
    if (host === 'twitchtranscripts.com') {
        var redirectUrl = "https://www." + host + request.uri;
        var response = {
            statusCode: 301,
            statusDescription: 'Moved Permanently',
            headers: {
                'cloudfront-functions': { value: 'generated-by-CloudFront-Functions' },
                'location': { value: redirectUrl }
            }
        };
        return response;
    }
    return request;
}
EOF
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