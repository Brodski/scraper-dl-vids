
output "name" {
  description = "API Gateway name"
  value       = aws_api_gateway_rest_api.api_gw_rest.name
}
output "api_url" {
  description = "API base url"
  value = aws_api_gateway_deployment.api_gw_deployment.invoke_url
}
output "cloudfront_domain_name" {
  value =  aws_cloudfront_distribution.lambda_distribution.domain_name
}
output website_name {
  value = local.website_name
}