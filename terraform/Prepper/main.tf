resource "aws_ecs_cluster" "my_cluster" {
  name = "my-cluster"
}

resource "aws_ecs_task_definition" "my_task" {
  family                   = "my-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "my-container",
      image = "my-docker-image",
      environment = [
        {
          name  = "MY_ENV_VARIABLE",
          value = "my-value"
        }
      ],
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.my_log_group.name
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "my_log_group" {
  name = "my-log-group"
  retention_in_days = 30 // Optional: Set the retention for your logs
}

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

resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "my-scheduled-rule"
  description         = "Trigger ECS task daily"
  schedule_expression = "rate(1 day)"
}


resource "aws_security_group" "my_sg" {
  name        = "my_sg"
  description = "ECS Security Group with no inbound traffic"
  vpc_id      = "vpc-0ee690d031cd7a0e6"  # Replace with your VPC ID

  # No inbound traffic
  # ingress {
  #   from_port   = 0
  #   to_port     = 0
  #   protocol    = "-1"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_cloudwatch_event_target" "ecs" {
  rule = aws_cloudwatch_event_rule.schedule.name
  arn  = aws_ecs_cluster.my_cluster.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.my_task.arn
    launch_type         = "FARGATE"
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
    }
  }
}

resource "aws_iam_policy" "ecs_events" {
  name        = "ecs_events"
  description = "A policy that allows ECS to be triggered by CloudWatch Events"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ecs:RunTask"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_events_attach" {
  policy_arn = aws_iam_policy.ecs_events.arn
  role       = aws_iam_role.ecs_execution_role.name
}
