# data "archive_file" "lambda_edge_code" {
#   type        = "zip"
#   output_path = "${path.module}/lambda_edge_code.zip"
#   source {
#     filename = "index.js"
#     content  = <<-EOF
#         export const handler = async (event) => {
#             const request = event.Records[0].cf.request;
#             const host = request.headers.host[0].value;
            
#             if (host === 'twitchtranscripts.com') {
#                 const redirectUrl = "https://www." + host + request.uri;
#                 return {
#                     status: '301',
#                     statusDescription: 'Moved Permanently',
#                     headers: {
#                         location: [{
#                             key: 'Location',
#                             value: redirectUrl
#                         }]
#                     }
#                 };
#             }
#             // Return the request unchanged
#             return request;
#         };
#     EOF
#   }
# }

# resource "aws_lambda_function" "edge_function" {
#   provider      = aws.useast1
#   function_name = "www_rewriter"
#   role          = aws_iam_role.lambda_edge_role.arn
#   handler       = "index.handler"
#   runtime       = "nodejs18.x"
#   memory_size   = 75
#   publish       = true
#   filename      = data.archive_file.lambda_edge_code.output_path
# }


# resource "aws_lambda_function" "edge_function" {
#   function_name = "www_rewriter"
#   role          = aws_iam_role.lambda_edge_role.arn
#   handler       = "index.handler"
#   runtime       = "nodejs18.x"
#   publish       = true

#   filename         = data.archive_file.lambda_edge_code.output_path
# }
