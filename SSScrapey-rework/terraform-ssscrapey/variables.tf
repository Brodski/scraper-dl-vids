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
    TWITCH_CLIENT_ID        = string
    TWITCH_CLIENT_SECRET    = string
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
variable "transcriber_model_size_override" {
  type = string
}
#############################
# Downloader  num instances #
#############################
variable "downloader_num_instances" {
  type = number
}
variable "dwn_batch_size_override" {
  type = string
}
########################
# Preper num instances #
########################
variable "prep_num_channels_override" {
  type = string
}
variable "prep_num_vod_per_channel_override" {
  type = string
}