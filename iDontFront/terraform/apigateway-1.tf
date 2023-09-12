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


##############################################################################
# {stage_name}/test
resource "aws_api_gateway_resource" "api_gw_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gw_rest.id
  parent_id   = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  path_part   = "test"
  # path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "path_method" {
  rest_api_id   = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id   = aws_api_gateway_resource.api_gw_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
#   depends_on = [module.navbar_footer_injector.aws_lambda_function]
  depends_on = [aws_lambda_function.nav_foot_lambda_fn]
  rest_api_id = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id = aws_api_gateway_resource.api_gw_resource.id
  http_method = "GET" # "GET", "POST", etc. or "ANY"

  integration_http_method = "POST" # uses "POST" always, even if the original client request was a GET, PUT, ect. b/c lambda is being "called" via a POST, (when Lambda integrations with API Gateway)
  type                    = "AWS_PROXY" # good idea / boilerplate type
  uri                     = aws_lambda_function.nav_foot_lambda_fn.invoke_arn
#   uri                     = module.navbar_footer_injector.lambda_nav_foot_invoke_arn 
}
