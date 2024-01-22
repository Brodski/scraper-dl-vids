# Downloader & Preper
resource "aws_iam_role" "ecs_execution_role" {
  name = "ecs_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }]
  })
}
resource "aws_iam_role" "ecs_events_role" {
  name = "ecs_events_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "events.amazonaws.com"
        },
      },
    ],
  })
}
# Grant CloudWatch Events permission to run tasks in ECS
resource "aws_iam_policy" "cloudwatch_events_ecs" {
  name = "cloudwatch_events_ecs_policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [      {
        Effect = "Allow",
        Action = [ "ecs:RunTask" ],
        Resource = "*"
      }]
  })
}
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole_terra"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }]
  })
}
resource "aws_iam_policy" "ecs_logs_policy" {
# resource "aws_iam_role_policy" "ecs_logs_policy" {
  name        = "ecs_logs_policy"
  # role        = aws_iam_role.ecs_execution_role.id
  # role          = aws_iam_role.ecs_task_execution_role.id 
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:CreateLogGroup"
        ],
        Effect = "Allow",
        Resource = "*"
      }]
  })
}
resource "aws_cloudwatch_event_permission" "allow_ecs" {
  action    = "events:PutEvents"
  principal = "*"
  statement_id = "allow-ecs"
}
resource "aws_iam_role_policy_attachment" "ecs_events" {
  role       = aws_iam_role.ecs_events_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceEventsRole"
}
resource "aws_iam_role_policy_attachment" "ecs_events_role_policy_attachment" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
resource "aws_iam_role_policy_attachment" "cloudwatch_logs_full_access" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}



# Transcriber 
# resource "aws_iam_role" "lambda_execution_role" {
#   name = "lambda_execution_role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [ {
#         Action = "sts:AssumeRole",
#         Effect = "Allow",
#         Principal = {
#           Service = "lambda.amazonaws.com"
#         }
#       }]
#   })
# }
# # Attach the AWSLambdaBasicExecutionRole policy to the role
# resource "aws_iam_role_policy_attachment" "lambda_exec_role_attach" {
#   role       = aws_iam_role.lambda_execution_role.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
# }
