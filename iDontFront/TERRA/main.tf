# Terrafrom's workspaces is bad for envs
# https://developer.hashicorp.com/terraform/cli/workspaces#when-not-to-use-multiple-workspaces

provider "aws" {
  region = "us-east-1"
  # alias  = "navbar_footer_injector__alias"
}
module "navbar_footer_injector" {
  source      = "./navbar_footer_injector"
  api_gateway_deployment_execution_arn = aws_api_gateway_deployment.api_gw_deployment.execution_arn
  iam_lambda_role_arn  = aws_iam_role.lambda_role.arn # value comes from iam.tf, variable set for lambda module
  api_gateway_rest_id = aws_api_gateway_rest_api.api_gw_rest.id
  api_gateway_rest_root_res_id = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  
}
module "second_test_lambda" {
  source      = "./second_test_lambda"
  api_gateway_deployment_execution_arn = aws_api_gateway_deployment.api_gw_deployment.execution_arn
  iam_lambda_role_arn  = aws_iam_role.lambda_role.arn 
  api_gateway_rest_id = aws_api_gateway_rest_api.api_gw_rest.id
  api_gateway_rest_root_res_id = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  
}

module "java_test_lambda" {
  source      = "./lambda_java_test"
  api_gateway_deployment_execution_arn = aws_api_gateway_deployment.api_gw_deployment.execution_arn
  iam_lambda_role_arn  = aws_iam_role.lambda_role.arn 
  api_gateway_rest_id = aws_api_gateway_rest_api.api_gw_rest.id
  api_gateway_rest_root_res_id = aws_api_gateway_rest_api.api_gw_rest.root_resource_id
  aws_lambda_role_arn = aws_iam_role.lambda_role.arn
}
output "lambda_functions_JAVA" {
  value = module.java_test_lambda
}


output "output_zip" {
  value = module.navbar_footer_injector.ouput_lambda_zip
}
output "navbar_footer_injector" {
  value = module.navbar_footer_injector
}


terraform {
  backend "s3" {
    bucket = "dev-dev-dev-my-terraform-state-bucket-money"
    key    = "path/dev/state.tfstate"
    region = "us-east-1"
  }
}
