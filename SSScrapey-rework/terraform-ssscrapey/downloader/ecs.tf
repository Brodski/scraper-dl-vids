resource "aws_ecs_cluster" "download_cluster" {
  name = "${var.sensitive_info.ENV}_download_cluster"

  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "download_task" {
  family                   = "${var.sensitive_info.ENV}_download_task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  # cpu                      = "2048"
  # memory                   = "4096"
  cpu                      = "1024"    # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-cpu-memory-error.html
  memory                   = "2048"
  execution_role_arn       = var.iam_role_ecs_exec_arn

  runtime_platform {
    # cpu_architecture        = "X86_64" #ARM64
    cpu_architecture        = "ARM64" #
    operating_system_family = "LINUX"
  }
  container_definitions = jsonencode([
    {
      name              = "downloader_container",
      essential         = true
      image             = var.docker_image
      environment = [
        { name = "AWS_SECRET_ACCESS_KEY"
          value =var.sensitive_info.MY_AWS_SECRET_ACCESS_KEY 
        },
        { name = "AWS_ACCESS_KEY_ID"
          value =var.sensitive_info.MY_AWS_ACCESS_KEY_ID 
        },
        { name = "ENV"
          value =var.sensitive_info.ENV 
        },
        { name = "DATABASE_HOST"
          value =var.sensitive_info.DATABASE_HOST 
        },
        { name = "DATABASE_USERNAME"
          value =var.sensitive_info.DATABASE_USERNAME 
        },
        { name = "DATABASE_PASSWORD"
          value =var.sensitive_info.DATABASE_PASSWORD 
        },
        { name = "DATABASE_PORT"
          value =var.sensitive_info.DATABASE_PORT 
        },
        { name = "DATABASE"
          value =var.sensitive_info.DATABASE 
        },
      ],
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-create-group  = "true"
          awslogs-group         = aws_cloudwatch_log_group.download_log_group.name
          # awslogs-group: "/ecs/fargate-example-logs",
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}
