# variable "iam_role_lambda_exec_arn" {
#   type = string
# }
variable "docker_image" {
  type = string
}
variable "transcriber_num_instances" {
  type = string
}
variable "transcriber_vods_per_instance" {
  type = string
}
variable "transcriber_schedule_cron" {
  type = string
}
variable "IS_VASTAI_CREATE_INSTANCE" {
  type = string
  default = "true"
}
variable "sensitive_info" {
  type = object({
    MY_AWS_SECRET_ACCESS_KEY   = string # transcriber/vastai uses MY_AWS...
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
