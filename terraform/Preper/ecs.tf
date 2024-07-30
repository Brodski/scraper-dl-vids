resource "aws_ecs_cluster" "preper_cluster" {
  name = "${var.sensitive_info.ENV}_preper_cluster"
}

resource "aws_ecs_task_definition" "preper_task" {
  family                   = "${var.sensitive_info.ENV}_preper_task" 
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  # cpu                      = "256" # 0.25 vCPU
  cpu                      = "1024"
  memory                   = "4096"
  execution_role_arn       = var.iam_role_ecs_exec_arn

  runtime_platform {
    cpu_architecture        = "X86_64" # ARM64
    operating_system_family = "LINUX"
  }
  container_definitions = jsonencode([
    {
      name              = "${var.sensitive_info.ENV}_preper_container"
      essential         = true # this is required. S/t with aws
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
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          # awslogs-group: "/ecs/fargate-example-logs",
          awslogs-create-group  = "true"
          awslogs-group         = aws_cloudwatch_log_group.preper_log_group.name
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# TO CREATE MANY OF THESE 
# TO CREATE MANY OF THESE 
# TO CREATE MANY OF THESE 
# TO CREATE MANY OF THESE 
#         desired_count   = 2
#         desired_count   = 2
#         desired_count   = 2
# resource "aws_ecs_service" "my_service" {
#   name            = "my_service"
#   cluster         = aws_ecs_cluster.my_cluster.id
#   task_definition = aws_ecs_task_definition.my_task.arn
#   desired_count   = 2
#   launch_type     = "FARGATE"

#   network_configuration {
#     subnets         = ["subnet-abcde123"]  # Replace with your subnet IDs
#     security_groups = ["sg-0123456789abcdef0"]  # Replace with your security group IDs
#     assign_public_ip = true
#   }
# }
