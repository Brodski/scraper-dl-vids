variable "lambda_name" {
  type        = string
  default     = "idontfront_app"
}
variable "ENV" {
  type = string
}
variable "docker_tag_name" {
  type = string
  default = "official_v2"
}

# PASSED FROM FILE
variable "sensitive_info" {
  type = object({
    BUCKET_DOMAIN             = string
    DATABASE_HOST             = string
    DATABASE_USERNAME         = string
    DATABASE_PASSWORD         = string
    DATABASE                  = string
    r53_acm_certificate_arn   = string
    r53_route_id              = string
  })
}