provider "aws" {
    region = "us-east-1"
}
terraform {
  backend "s3" {
    bucket = "scraper-transcriptions-terraform-states"
    region = "us-east-1"
    # key set at command line
  }
}

module "preper" {
    source = "./preper"
    iam_role_ecs_events_arn  = aws_iam_role.ecs_events_role.arn 
    iam_role_ecs_exec_arn    = aws_iam_role.ecs_task_execution_role.arn
    sg_name_id               = aws_security_group.my_sg.id
    sensitive_info           = var.sensitive_info
    preper_schedule_cron     = var.preper_schedule_cron
    docker_image             = var.preper_docker_image # "cbrodski/preper:official_v2_prod" or official_v2_dev
}

module "downloader" {
    source                      = "./downloader"
    iam_role_ecs_events_arn     = aws_iam_role.ecs_events_role.arn 
    iam_role_ecs_exec_arn       = aws_iam_role.ecs_task_execution_role.arn
    sg_name_id                  = aws_security_group.my_sg.id
    sensitive_info              = var.sensitive_info
    downloader_schedule_cron    = var.downloader_schedule_cron
    docker_image                = var.downloader_docker_image
    downloader_num_instances       = var.downloader_num_instances
    dwn_batch_size_override     = var.dwn_batch_size_override
}

module "transcriber" {
    source                      = "./transcriber"
    sensitive_info              = var.sensitive_info
    transcriber_schedule_cron   = var.transcriber_schedule_cron
    transcriber_num_instances   = var.transcriber_num_instances # Note, we also have a muliplier in `/SScrapey-rework/.env_public_prod`
    transcriber_vods_per_instance = var.transcriber_vods_per_instance
    docker_image                = var.transcriber_docker_image
}
