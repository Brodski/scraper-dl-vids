resource "aws_iam_role" "lambda_writer_role" {
  name = "lambda_writer_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = ["apigateway.amazonaws.com", "lambda.amazonaws.com"]
        },
        Effect = "Allow",
        Sid    = ""
      }
    ]
  })
}

# allow writing logs to CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_writer_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

