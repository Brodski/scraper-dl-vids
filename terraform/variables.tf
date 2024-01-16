variable "sensitive_info" {
  type = object({
    AWS_SECRET_ACCESS_KEY   = string
    AWS_ACCESS_KEY_ID       = string
    ENV                     = string
    DATABASE_HOST           = string
    DATABASE_USERNAME       = string
    DATABASE_PASSWORD       = string
    DATABASE                = string
  })
}
