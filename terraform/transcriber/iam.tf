resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [ {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }]
  })
}
# Attach the AWSLambdaBasicExecutionRole policy to the role
resource "aws_iam_role_policy_attachment" "lambda_exec_role_attach" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}




# resource "aws_iam_role_policy" "lambda_policy" {
#   name = "lambda_policy"
#   role = aws_iam_role.lambda_execution_role.id

#   policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [{
#       Action = [
#         "logs:CreateLogGroup",
#         "logs:CreateLogStream",
#         "logs:PutLogEvents"
#       ],
#       Effect = "Allow",
#       Resource = "arn:aws:logs:*:*:*"
#     }]
#   })
# }