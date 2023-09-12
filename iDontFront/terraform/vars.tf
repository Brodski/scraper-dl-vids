# r53_lambda_full_domain  = "party-dev.bski.one"
# r53_s3_asset_full_domain = "s3test-dev.bski.one"
# s3_asset_bucket_name = "s3-dev-assets-1213e144-b60d"
# s3_log_bucket_name = "dev-my-log-bucket-name-xzxzxzxz"
# apigateway_name = "api-name-test"


variable "lambda_name" {
  description = "nav_foot_lambda"
  type        = string
  default     = "nav_foot_lambda_fn_DEV"
}
variable "r53_lambda_full_domain" {
  description = "r53_lambda_full_domain"
  type        = string
  default     = "captions.bski.one"
}
variable "r53_s3_asset_full_domain" {
  description = "r53_s3_asset_full_domain"
  type        = string
  default     = "cc-assets.bski.one"
}
variable "s3_asset_bucket_name" {
  description = "s3_asset_bucket_name"
  type        = string
  default     = "s3-cc-assets-best-bucket-bski"
}
variable "s3_log_bucket_name" {
  description = "s3_log_bucket_name"
  type        = string
  default     = "s3-cc-logs-usa-number-1-bski"
}
variable "apigateway_name" {
  description = "apigateway_name"
  type        = string
  default     = "cc-api-gateway"
}

##############################################
variable "r53_route_id" {
  description = "The AWS region"
  type = string
  default = "lol-no"
}

variable "r53_acm_certificate_arn" {
  description = "The r53 cert arn"
  type = string
  default = "arn:1234567890"
}

