# V1 API Gateway
# V1 API Gateway
# V1 API Gateway
# V1 API Gateway
resource "aws_api_gateway_rest_api" "api_gw_rest" {
  name        = "${var.ENV}_idontfront_api_gw"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

##### 0 #####
resource "aws_api_gateway_deployment" "api_gw_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_gw_rest.id
  stage_name  = "v1"
  triggers = {
    redeployment = timestamp()
  }
}
resource "aws_api_gateway_method" "path_root" {
  rest_api_id   = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id   = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "root_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id             = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  http_method             = aws_api_gateway_method.path_root.http_method
  integration_http_method = "POST"     # uses "POST" always, even if the original client request was a GET, PUT, ect. b/c lambda is being "called" via a POST, (when Lambda integrations with API Gateway)
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.idontfront_lambda.invoke_arn
}

##### 1 #####
# {stage_name}/{proxy+}
resource "aws_api_gateway_resource" "api_gw_resource_proxy" {
  rest_api_id = aws_api_gateway_rest_api.api_gw_rest.id
  parent_id   = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  path_part   = "{proxy+}"
}
resource "aws_api_gateway_method" "proxy_any" {
  rest_api_id   = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id   = aws_api_gateway_resource.api_gw_resource_proxy.id
  http_method   = "GET"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "proxy_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id             = aws_api_gateway_resource.api_gw_resource_proxy.id
  http_method             = "GET"
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.idontfront_lambda.invoke_arn
}
