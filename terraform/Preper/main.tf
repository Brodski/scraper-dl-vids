
provider "aws" {
  region = "us-east-1"
}

# data "archive_file" "lambda_zip" {
#     type = "zip"
#     output_path = "${path.module}/output_code.zip"
#     source_dir = "${path.module}/auto-vast-runner"
# }
resource "aws_ecs_cluster" "my_cluster" {
  name = "my-cluster"
}


resource "aws_ecs_task_definition" "my_task" {
  family                   = "my-task" #some name unique
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  # cpu                      = "256" # 0.25 vCPU
  cpu                      = "1024"
  memory                   = "4096"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  # execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  runtime_platform {
    cpu_architecture        = "X86_64" # ARM64
    operating_system_family = "LINUX"
  }
  container_definitions = jsonencode([
    {
      name              = "my-container",
      image             = "cbrodski/ssscrapey:v2.5"
      essential         = true
      # image             = "cbrodski/preper:official_v1"
      # memory            = "4096"  # Hard limit - 4096 MB
      # memoryReservation = "300"  # Soft limit - 300 MB
      environment = [
        {
          name  = "MY_ENV_VARIABLE",
          value = "my-value"
        }
      ],
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          # awslogs-group: "/ecs/fargate-example-logs",
          awslogs-create-group  = "true"
          awslogs-group         = aws_cloudwatch_log_group.my_log_group.name
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_event_target" "ecs" {
  rule        = aws_cloudwatch_event_rule.schedule.name
  arn         = aws_ecs_cluster.my_cluster.arn
  # role_arn    = aws_iam_role.ecs_task_execution_role.arn 
  role_arn    = aws_iam_role.ecs_events_role.arn 
  input       = jsonencode({})
  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.my_task.arn
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
      security_groups = [aws_security_group.my_sg.id]
      assign_public_ip = true
    }
  }
}

resource "aws_cloudwatch_log_group" "my_log_group" {
  name = "my-log-group"
  retention_in_days = 30 // Optional: Set the retention for your logs
}

resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "my-scheduled-rule"
  description         = "Trigger ECS task daily"
  # schedule_expression = "rate(1 day)"
  schedule_expression = "cron(*/10 * * * ? *)"
  # schedule_expression = "cron(30 12 * * ? *)" # daily at 11:00am UTC
}


resource "aws_security_group" "my_sg" {
  name        = "my_sg"
  description = "ECS Security Group with no inbound traffic"
  vpc_id      = "vpc-0ee690d031cd7a0e6"

  # No inbound traffic
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# cbrodski/preper:official_v1
# cbrodski/ssscrapey:v2.5

















resource "aws_iam_role" "ecs_execution_role" {
  name = "ecs_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
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
    Statement = [
      {
        Effect = "Allow",
        Action = [ "ecs:RunTask" ],
        Resource = "*" #[ aws_ecs_task_definition.my_task.arn ]
      }
    ]
  })
}

#log 
resource "aws_iam_policy" "ecs_logs_policy" {
  name        = "ecs_logs_policy"
  description = "Allow ECS tasks to interact with any CloudWatch Logs"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:CreateLogGroup"
        ],
        Effect = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_cloudwatch_event_permission" "allow_ecs" {
  action    = "events:PutEvents"
  principal = "*"
  statement_id = "allow-ecs"
}

# https://www.terraform.io/docs/providers/aws/r/iam_role_policy_attachment.html
resource "aws_iam_role_policy_attachment" "ecs_events" {
  role       = aws_iam_role.ecs_events_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceEventsRole"
  # policy_arn = aws_iam_policy.ecs_events_policy.arn
}
# resource "aws_iam_role_policy_attachment" "cloudwatch_events_ecs_policy_attachment" {
#   role       = aws_iam_role.ecs_events_role.name
#   policy_arn = aws_iam_policy.cloudwatch_events_ecs.arn
# }
resource "aws_iam_role_policy_attachment" "ecs_events_role_policy_attachment" {
  role       = aws_iam_role.ecs_execution_role.name
  # role       = aws_iam_role.ecs_events_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
# resource "aws_iam_role_policy_attachment" "ecs_execution_role_logs_attachment" {
#   role       = aws_iam_role.ecs_execution_role.name
#   policy_arn = aws_iam_policy.ecs_logs_policy.arn
# }




resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole_terra"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs_full_access" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}













