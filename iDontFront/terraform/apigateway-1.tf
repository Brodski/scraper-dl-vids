# V1 API Gateway
# V1 API Gateway
# V1 API Gateway
# V1 API Gateway
resource "aws_api_gateway_rest_api" "api_gw_rest" {
  name        = var.apigateway_name
  description = "iDontFront-gw"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "api_gw_deployment" {
  depends_on = [ aws_api_gateway_integration.root_lambda, aws_api_gateway_integration.proxy_lambda ]
  rest_api_id = aws_api_gateway_rest_api.api_gw_rest.id
  stage_name  = "v1"
}

##############################################################################
# Root resource integration with Lambda
resource "aws_api_gateway_method" "path_root" {
  rest_api_id   = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id   = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "root_lambda" {
  depends_on = [aws_lambda_function.idontfront_lambda]
  rest_api_id = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  http_method = "GET" # "GET", "POST", etc. or "ANY"

  integration_http_method = "POST" # uses "POST" always, even if the original client request was a GET, PUT, ect. b/c lambda is being "called" via a POST, (when Lambda integrations with API Gateway)
  type                    = "AWS_PROXY" # good idea / boilerplate type
  uri                     = aws_lambda_function.idontfront_lambda.invoke_arn
}

##############################################################################
# Proxy resource for all other paths
# {stage_name}/test
resource "aws_api_gateway_resource" "api_gw_resource_proxy" {
  rest_api_id = aws_api_gateway_rest_api.api_gw_rest.id
  parent_id   = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  # path_part   = "test"
  path_part   = "{proxy+}"
}
resource "aws_api_gateway_method" "proxy_any" {
  rest_api_id   = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id   = aws_api_gateway_resource.api_gw_resource_proxy.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "proxy_lambda" {
  rest_api_id = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id = aws_api_gateway_resource.api_gw_resource_proxy.id
  http_method = "GET"
  # http_method = aws_api_gateway_method.proxy_any.http_method

  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.idontfront_lambda.invoke_arn
}












output "name" {
  description = "API Gateway name"
  value       = aws_api_gateway_rest_api.api_gw_rest.name
}

output "api_url" {
  description = "API base url"
  value = aws_api_gateway_deployment.api_gw_deployment.invoke_url
}
