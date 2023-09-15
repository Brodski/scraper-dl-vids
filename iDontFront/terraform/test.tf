# resource "aws_api_gateway_rest_api" "my_api" {
#   name        = "MyAPI"
#   description = "My API Gateway with root and proxy resources"
#   endpoint_configuration {
#     types = ["REGIONAL"]
#   }
# }

# # Proxy resource for all other paths
# resource "aws_api_gateway_resource" "proxy123" {
#   rest_api_id = aws_api_gateway_rest_api.my_api.id
#   parent_id   = aws_api_gateway_rest_api.my_api.root_resource_id
#   path_part   = "{proxy+}"
# }
# #########################
# # Root resource integration with Lambda
# resource "aws_api_gateway_method" "root_any" {
#   rest_api_id   = aws_api_gateway_rest_api.my_api.id
#   resource_id   = aws_api_gateway_rest_api.my_api.root_resource_id
#   http_method   = "ANY"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_integration" "root_lambda" {
#   rest_api_id = aws_api_gateway_rest_api.my_api.id
#   resource_id = aws_api_gateway_rest_api.my_api.root_resource_id
#   http_method = aws_api_gateway_method.root_any.http_method

#   type                    = "AWS_PROXY"
#   integration_http_method = "POST"
#   uri                     = aws_lambda_function.my_lambda.invoke_arn
# }

# ##################################
# resource "aws_api_gateway_method" "proxy_any" {
#   rest_api_id   = aws_api_gateway_rest_api.my_api.id
#   resource_id   = aws_api_gateway_resource.proxy123.id
#   http_method   = "ANY"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_integration" "proxy_lambda" {
#   rest_api_id = aws_api_gateway_rest_api.my_api.id
#   resource_id = aws_api_gateway_resource.proxy123.id
#   http_method = aws_api_gateway_method.proxy_any.http_method

#   type                    = "AWS_PROXY"
#   integration_http_method = "POST"
#   uri                     = aws_lambda_function.my_lambda.invoke_arn
# }
# #####################################
# resource "aws_lambda_function" "my_lambda" {
#   ...
#   # Remaining lambda configuration
#   ...
# }

# resource "aws_api_gateway_deployment" "my_api_deployment" {
#   rest_api_id = aws_api_gateway_rest_api.my_api.id
#   stage_name  = "v1"
#   depends_on  = [
#     aws_api_gateway_method.root_any,
#     aws_api_gateway_integration.root_lambda,
#     aws_api_gateway_method.proxy_any,
#     aws_api_gateway_integration.proxy_lambda
#   ]
# }
