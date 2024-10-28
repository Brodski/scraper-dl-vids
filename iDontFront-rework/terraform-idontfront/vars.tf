variable "lambda_name" {
  type        = string
  default     = "idontfront_app"
}
variable "URL_CANONICAL_BASE" {
  type = string
}
variable "ENV" {
  type = string
}
variable "docker_tag_name" {
  type = string
}

# PASSED FROM FILE
variable "sensitive_info" {
  type = object({
    BUCKET_DOMAIN             = string
    DATABASE_HOST             = string
    DATABASE_USERNAME         = string
    DATABASE_PASSWORD         = string
    DATABASE_PORT             = string
    DATABASE                  = string
    r53_acm_certificate_arn   = string
    r53_route_id              = string
  })
}