# ROUTE 53 FOR LAMBDA
# resource "aws_route53_zone" "example_zone" {
#   name = "example.com"  # replace with your domain name
# }
resource "aws_route53_record" "lambda_record" {
  # zone_id = aws_route53_zone.example_zone.zone_id
  zone_id = "Z0557754VK24H4AZRJ6R"
  name    = var.r53_lambda_full_domain
  type    = "A"
  alias {
    name                   = aws_cloudfront_distribution.lambda_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.lambda_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}


# resource "aws_route53_record" "s3_asset_record" {
#   zone_id = "Z0557754VK24H4AZRJ6R" # copy and pasted from aws
#   name    = var.r53_s3_asset_full_domain 
#   type    = "A"
#   alias {
#     name                   = aws_cloudfront_distribution.s3_distribution.domain_name
#     zone_id                = aws_cloudfront_distribution.s3_distribution.hosted_zone_id
#     evaluate_target_health = false
#   }
# }