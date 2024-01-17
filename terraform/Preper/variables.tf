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
