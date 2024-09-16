resource "aws_iam_role" "idont_writer_role" {
  name = "idont_writer_role_${var.ENV}"
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
  role       = aws_iam_role.idont_writer_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

###################################
resource "aws_iam_role" "lambda_edge_role" {
  name = "edge_${var.ENV}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = ["lambda.amazonaws.com", "edgelambda.amazonaws.com", "apigateway.amazonaws.com"]
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "lambda_edge_policy" {
  role       = aws_iam_role.lambda_edge_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}