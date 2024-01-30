# ROUTE 53 FOR LAMBDA
# resource "aws_route53_zone" "example_zone" {
#   name = "example.com"  # replace with your domain name
# }
resource "aws_route53_record" "lambda_record" {
  # zone_id = aws_route53_zone.example_zone.zone_id
  zone_id = var.r53_route_id
  name    = var.r53_lambda_full_domain
  type    = "A"
  alias {
    name                   = aws_cloudfront_distribution.lambda_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.lambda_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}