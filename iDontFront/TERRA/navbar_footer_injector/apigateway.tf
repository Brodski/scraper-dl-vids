
# {stage_name}/test
resource "aws_api_gateway_resource" "api_gw_resource" {
  rest_api_id = var.api_gateway_rest_id
  parent_id   = var.api_gateway_rest_root_res_id
  path_part   = "test"
  # path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "path_method" {
  rest_api_id   = var.api_gateway_rest_id
  resource_id   = aws_api_gateway_resource.api_gw_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
#   depends_on = [module.navbar_footer_injector.aws_lambda_function]
  depends_on = [aws_lambda_function.nav_foot_lambda_fn]
  rest_api_id = var.api_gateway_rest_id
  resource_id = aws_api_gateway_resource.api_gw_resource.id
  http_method = "GET" # "GET", "POST", etc. or "ANY"

  integration_http_method = "POST" # uses "POST" always, even if the original client request was a GET, PUT, ect. b/c lambda is being "called" via a POST, (when Lambda integrations with API Gateway)
  type                    = "AWS_PROXY" # good idea / boilerplate type
  uri                     = aws_lambda_function.nav_foot_lambda_fn.invoke_arn
#   uri                     = module.navbar_footer_injector.lambda_nav_foot_invoke_arn 
}
