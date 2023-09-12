variable "s3_asset_bucket_name" {
  description = "s3_asset_bucket_name"
  type        = string
}
variable "r53_s3_asset_full_domain" {
  description = "r53_s3_asset_full_domain"
  type        = string
}
variable "r53_acm_certificate_arn" {
  description = "r53_acm_certificate_arn"
  type        = string
}
variable "r53_route_id" {
  description = "r53_route_id"
  type        = string
}
variable "s3_log_bucket_name" {
  description = "s3_log_bucket_name"
  type        = string
}
variable "s3_log_bucket_resource" {
  description = "s3_log_bucket_resource"
  type        = string
}