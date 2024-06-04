# V1 API Gateway
# V1 API Gateway
# V1 API Gateway
# V1 API Gateway
resource "aws_api_gateway_rest_api" "api_gw_rest" {
  name        = "${var.ENV}_mini_image_api_gw"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  binary_media_types = ["*/*"]
}

##### 0 #####
resource "aws_api_gateway_deployment" "api_gw_deployment" {
  depends_on = [aws_api_gateway_integration.root_lambda]
  rest_api_id = aws_api_gateway_rest_api.api_gw_rest.id
  stage_name  = "v1"
  triggers = {
    redeployment = timestamp()
  }
}
resource "aws_api_gateway_method" "path_root" {
  rest_api_id   = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id   = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "root_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id             = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  http_method             = aws_api_gateway_method.path_root.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.mini_image_lambda.invoke_arn
  content_handling        = "CONVERT_TO_BINARY" # GET images (favicon)
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
  http_method   = "ANY"
  authorization = "NONE"
}
resource "aws_api_gateway_integration" "proxy_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api_gw_rest.id
  resource_id             = aws_api_gateway_resource.api_gw_resource_proxy.id
  http_method             = aws_api_gateway_method.proxy_any.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.mini_image_lambda.invoke_arn
  content_handling        = "CONVERT_TO_BINARY" # POST images (return mini'd images)
}
