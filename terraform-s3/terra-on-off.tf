# Me: Is there an AWS service that can instantiate a few servers daily then shut them all down when no longer needed?
# ChatGPT4: Yes. [...]
# Can you provide me an example terraform file that does exactly that?
# ChatGPT4: Yes:
provider "aws" {
  region = "<your-aws-region>"
}

resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7" # Example Amazon Linux 2 AMI ID; replace with your desired AMI ID
  instance_type = "t2.micro"
}

resource "aws_iam_role" "lambda_ec2_role" {
  name = "lambda_ec2_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_ec2_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
  role       = aws_iam_role.lambda_ec2_role.name
}

resource "aws_lambda_function" "start_stop_instance" {
  function_name = "start_stop_instance"
  handler       = "index.handler"
  role          = aws_iam_role.lambda_ec2_role.arn
  runtime       = "nodejs14.x"

  filename = "<your_lambda_function_zip>"

  environment {
    variables = {
      INSTANCE_ID = aws_instance.example.id
    }
  }
}

resource "aws_cloudwatch_event_rule" "daily_start" {
  name                = "daily_start"
  description         = "Trigger Lambda to start the EC2 instance daily"
  schedule_expression = "cron(0 12 * * ? *)" # Start at 12:00 UTC daily; adjust as needed
}

resource "aws_cloudwatch_event_rule" "daily_stop" {
  name                = "daily_stop"
  description         = "Trigger Lambda to stop the EC2 instance daily"
  schedule_expression = "cron(0 20 * * ? *)" # Stop at 20:00 UTC daily; adjust as needed
}

resource "aws_cloudwatch_event_target" "start_instance" {
  rule      = aws_cloudwatch_event_rule.daily_start.name
  target_id = "start_instance"
  arn       = aws_lambda_function.start_stop_instance.arn
}

resource "aws_cloudwatch_event_target" "stop_instance" {
  rule      = aws_cloudwatch_event_rule.daily_stop.name
  target_id = "stop_instance"
  arn       = aws_lambda_function.start_stop_instance.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_start" {
  statement_id  = "AllowExecutionFromCloudWatchStart"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.start_stop_instance.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_start.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_stop" {
  statement_id  = "AllowExecutionFromCloudWatchStop"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.start_stop_instance.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_stop.arn
}


## LAMBDA
# I'm assuming you're using Node.js as the runtime for your Lambda function. 
# Make sure to create a Lambda function (e.g., index.js) with a handler that 
# starts and stops the EC2 instance based on the CloudWatch Event trigger.
# const AWS = require('aws-sdk');
# const ec2 = new AWS.EC2();

# exports.handler = async (event) => {
#   const instanceId = process.env.INSTANCE_ID;

#   if (event.resources[0].includes('daily_start')) {
#     await startInstance(instanceId);
#   } else if (event.resources[0].includes('daily_stop')) {
#     await stopInstance(instanceId);
#   }
# };

# async function startInstance(instanceId) {
#   const params = {
#     InstanceIds: [instanceId]
#   };

#   try {
#     await ec2.startInstances(params).promise();
#     console.log(`Instance ${instanceId} started successfully.`);
#   } catch (error) {
#     console.error(`Error starting instance ${instanceId}:`, error);
#   }
# }

# async function stopInstance(instanceId) {
#   const params = {
#     InstanceIds: [instanceId]
#   };

#   try {
#     await ec2.stopInstances(params).promise();
#     console.log(`Instance ${instanceId} stopped successfully.`);
#   } catch (error) {
#     console.error(`Error stopping instance ${instanceId}:`, error);
#   }
# }
