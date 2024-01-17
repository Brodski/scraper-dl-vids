provider "aws" {
    region = "us-east-1"
}

module "preper" {
    source = "./preper"
    iam_role_ecs_events_arn  = aws_iam_role.ecs_events_role.arn 
    iam_role_ecs_exec_arn    = aws_iam_role.ecs_task_execution_role.arn
    sg_name_id               = aws_security_group.my_sg.id
    docker_image             = "cbrodski/preper:official_v2"
    sensitive_info           = var.sensitive_info
}

# module "downloader" {
#     source                   = "./downloader"
#     iam_role_ecs_events_arn  = aws_iam_role.ecs_events_role.arn 
#     iam_role_ecs_exec_arn    = aws_iam_role.ecs_task_execution_role.arn
#     sg_name_id               = aws_security_group.my_sg.id
    # docker_image             = "cbrodski/downloader:official_v2"
#     sensitive_info          = var.sensitive_info
# }

# module "transcriber" {
#     source                      = "./transcriber"
#     sensitive_info              = var.sensitive_info
#     iam_role_lambda_exec_arn    = aws_iam_role.lambda_execution_role.arn
# }
