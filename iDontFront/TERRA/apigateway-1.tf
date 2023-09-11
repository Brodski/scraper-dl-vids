# V1 API Gateway
# V1 API Gateway
# V1 API Gateway
# V1 API Gateway
resource "aws_api_gateway_rest_api" "api_gw_rest" {
  name        = var.apigateway_name
  description = "API - very cool 123"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "api_gw_deployment" {
  # depends_on = [aws_api_gateway_integration.lambda]
  rest_api_id = aws_api_gateway_rest_api.api_gw_rest.id
  stage_name  = "dev"
}


output "name" {
  description = "API Gateway name"
  value       = aws_api_gateway_rest_api.api_gw_rest.name
}

output "api_url" {
  description = "API base url"
  value = aws_api_gateway_deployment.api_gw_deployment.invoke_url
}