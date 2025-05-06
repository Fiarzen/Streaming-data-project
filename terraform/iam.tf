#lambda
resource "aws_iam_role" "lambda_role" {
  name_prefix        = "role-api-lambda"
  assume_role_policy = <<EOF
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "sts:AssumeRole"
                ],
                "Principal": {
                    "Service": [
                        "lambda.amazonaws.com"
                    ]
                }
            }
        ]
    }
    EOF
}




resource "aws_iam_role_policy" "allow_sns_publish" {
  name = "allow-publish-to-guardian-content"
  role = aws_iam_role.lambda_role.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "sns:Publish",
        Resource = "arn:aws:sns:eu-west-2:289831833467:guardian_content"
      }
    ]
  })
}


resource "aws_iam_policy" "lambda_logging" {
  name = "lambda-logging"
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        } 
    ]
} 
EOF
}



resource "aws_iam_role_policy_attachment" "attach_logging_access" { 
  role = aws_iam_role.lambda_role.name 
  policy_arn = aws_iam_policy.lambda_logging.arn 
  }


resource "aws_iam_role_policy" "lambda_sqs_publish" {
  name = "lambda_sqs_publish"
  role = aws_iam_role.lambda_role.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:SendMessage"
        ],
        Resource = aws_sqs_queue.guardian_content.arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_send_to_sqs" {
  name = "lambda_send_to_sqs"
  role = aws_iam_role.lambda_role.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:SendMessage"
        ],
        Resource = aws_sqs_queue.guardian_content.arn
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "attach_sqs_publish_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.sqs_publish_policy.arn
}

data "aws_iam_role" "lambda_role" {
  name = aws_iam_role.lambda_role.name
}

resource "aws_iam_policy" "sqs_publish_policy" {
  name   = "GuardianContentSQSPublishPolicy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "sqs:SendMessage",
        Resource = aws_sqs_queue.guardian_content.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_sqs_policy" {
  role       = data.aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.sqs_publish_policy.arn
}


