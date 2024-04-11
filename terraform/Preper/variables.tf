variable "iam_role_ecs_events_arn" {
    type        = string
}
variable "iam_role_ecs_exec_arn" {
    type        = string
}
variable "sg_name_id" {
    type        = string
}
variable "docker_image" {
  type = string
}
variable "preper_schedule_cron" {
  type = string
}
variable "sensitive_info" {
  type = object({
    MY_AWS_SECRET_ACCESS_KEY   = string
    MY_AWS_ACCESS_KEY_ID       = string
    ENV                     = string
    DATABASE_HOST           = string
    DATABASE_USERNAME       = string
    DATABASE_PASSWORD       = string
    DATABASE_PORT           = string
    DATABASE                = string
    VAST_API_KEY            = string
  })
}
