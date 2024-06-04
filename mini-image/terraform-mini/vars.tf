variable "lambda_name" {
  type        = string
  default     = "mini_image_app"
}
variable "ENV" {
  type = string
}

# PASSED FROM FILE
variable "sensitive_info" {
  type = object({
    r53_acm_certificate_arn   = string
    r53_route_id              = string
  })
}