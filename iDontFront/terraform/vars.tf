# r53_lambda_full_domain  = "party-dev.bski.one"
# r53_s3_asset_full_domain = "s3test-dev.bski.one"
# s3_asset_bucket_name = "s3-dev-assets-1213e144-b60d"
# apigateway_name = "api-name-test"


variable "lambda_name" {
  description = "nav_foot_lambda"
  type        = string
  default     = "idontfront_app"
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
variable "apigateway_name" {
  description = "apigateway_name"
  type        = string
  default     = "idontfront-api-gateway"
}

##############################################
variable "r53_route_id" {
  description = "The AWS region"
  type = string
}

variable "r53_acm_certificate_arn" {
  description = "The r53 cert arn"
  type = string
}

