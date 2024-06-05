resource "aws_iam_role" "mini_image_role" {
  name = "mini_image_${var.ENV}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [ {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = ["apigateway.amazonaws.com", "lambda.amazonaws.com"]
        },
        Sid    = ""
      } ]
  })
}

# allow writing logs to CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.mini_image_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

