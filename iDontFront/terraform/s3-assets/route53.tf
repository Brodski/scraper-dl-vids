
resource "aws_route53_record" "s3_asset_record" {
  zone_id = var.r53_route_id # copy and pasted from aws
  name    = var.r53_s3_asset_full_domain 
  type    = "A"
  alias {
    name                   = aws_cloudfront_distribution.s3_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.s3_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}