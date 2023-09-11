variable "lambda_name" {
  description = "nav_foot_lambda"
  type        = string
  default     = "nav_foot_lambda_fn_DEV"
}
variable "iam_lambda_role_arn" {
  description = "The ARN of the Lambda IAM role"
  type        = string
}
variable "api_gateway_deployment_execution_arn" {
  description = "The ARN of API GW Exec arn"
  type        = string
}
variable "api_gateway_rest_id" {
  description = "The ID of the API GW"
  type        = string
}
variable "api_gateway_rest_root_res_id" {
  description = "The ID of the API GW root resource"
  type        = string
}
