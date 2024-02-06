variable "sensitive_info" {
  type = object({
    MY_AWS_SECRET_ACCESS_KEY   = string
    MY_AWS_ACCESS_KEY_ID       = string
    ENV                     = string
    DATABASE_HOST           = string
    DATABASE_USERNAME       = string
    DATABASE_PASSWORD       = string
    DATABASE                = string
    VAST_API_KEY            = string
  })
}
variable "preper_schedule_cron" {
  type = string
}
variable "downloader_schedule_cron" {
  type = string
}
variable "transcriber_schedule_cron" {
  type = string
}