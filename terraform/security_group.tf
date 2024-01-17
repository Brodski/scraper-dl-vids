resource "aws_security_group" "my_sg" {
  name        = "my_sg"
  description = "ECS Security Group with no inbound traffic"
  vpc_id      = "vpc-0ee690d031cd7a0e6"

  # No inbound traffic -> comment out ingress
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Allow all outbound traffic
  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


