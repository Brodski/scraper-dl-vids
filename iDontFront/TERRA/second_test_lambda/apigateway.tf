# {stage_name}/test2
resource "aws_api_gateway_resource" "api_gw_resource_2" {
  rest_api_id = var.api_gateway_rest_id
  parent_id   = var.api_gateway_rest_root_res_id
  path_part   = "test2"
  # path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "path_method_2" {
  rest_api_id   = var.api_gateway_rest_id
  resource_id   = aws_api_gateway_resource.api_gw_resource_2.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  depends_on = [aws_lambda_function.lambda_fn_test_TWO]
  rest_api_id = var.api_gateway_rest_id
  resource_id = aws_api_gateway_resource.api_gw_resource_2.id
  http_method = "GET"

  integration_http_method = "POST" 
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.lambda_fn_test_TWO.invoke_arn
}
