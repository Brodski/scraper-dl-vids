resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "${var.sensitive_info.ENV}_download_schedule"
  description         = "Trigger downloader on ECS task daily"
  schedule_expression = var.downloader_schedule_cron
}
resource "aws_cloudwatch_event_target" "ecs" {
  rule        = aws_cloudwatch_event_rule.schedule.name
  arn         = aws_ecs_cluster.download_cluster.arn
  role_arn    = var.iam_role_ecs_events_arn
  input       = jsonencode({})
  ecs_target {
    task_count          = var.downloader_aws_bs_id
    task_definition_arn = aws_ecs_task_definition.download_task.arn
    launch_type         = "FARGATE"
    platform_version    = "LATEST"

    network_configuration {
      subnets = [
        "subnet-074266770b3907a40",
        "subnet-043e9152b83b9f7a6",
        "subnet-0df87e95c1aa86d23",
        "subnet-03439b2eec2465d4f",
        "subnet-03a939bf02aaff07d",
        "subnet-0468a4b6cab55c7af"
      ]
      security_groups = [var.sg_name_id]
      assign_public_ip = true # required to pull from docker
    }
  }
}