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
##########
# Docker #
##########
variable "preper_docker_image" {
  type = string
}
variable "downloader_docker_image" {
  type = string
}
variable "transcriber_docker_image" {
  type = string
}
#############
# Scheduler #
#############
variable "preper_schedule_cron" {
  type = string
}
variable "downloader_schedule_cron" {
  type = string
}
variable "transcriber_schedule_cron" {
  type = string
}
#############################
# Transcriber num instances #
#############################
variable "transcriber_num_instances" {
  type = string
}
variable "transcriber_vods_per_instance" {
  type = string
}
#############################
# Downloader  num instances #
#############################
variable "downloader_aws_bs_id" {
  type = number
}