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
    docker_image             = "cbrodski/preper:official_v2"
}

module "downloader" {
    source                      = "./downloader"
    iam_role_ecs_events_arn     = aws_iam_role.ecs_events_role.arn 
    iam_role_ecs_exec_arn       = aws_iam_role.ecs_task_execution_role.arn
    sg_name_id                  = aws_security_group.my_sg.id
    sensitive_info              = var.sensitive_info
    downloader_schedule_cron    = var.downloader_schedule_cron
    docker_image                = "cbrodski/downloader:official_v2"
}

module "transcriber" {
    source                      = "./transcriber"
    sensitive_info              = var.sensitive_info
    transcriber_schedule_cron   = var.transcriber_schedule_cron
    docker_image                = "cbrodski/transcriber:official_v2"
}
