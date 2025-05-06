#lambda
resource "aws_iam_role" "lambda_role" {
  name_prefix        = "role-totes-lambda"
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


resource "aws_iam_policy" "lambda_secret_access" {
  name = "lambda-secret-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = ["secretsmanager:GetSecretValue"],
      Effect   = "Allow",
      Resource = aws_secretsmanager_secret.api_credentials.arn
    }]
  })
}

resource "aws_iam_policy" "lambda_get_parameter" {
  name = "lambda-parameter-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = ["ssm:GetParameter", "ssm:PutParameter", "sns:Publish"]
      Effect   = "Allow",
      Resource = ["arn:aws:ssm:eu-west-2:216989110647:parameter/*"]
    }]
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


resource "aws_iam_role_policy_attachment" "attach_secret_access" { 
  role = aws_iam_role.lambda_role.name 
  policy_arn = aws_iam_policy.lambda_secret_access.arn 
  }

resource "aws_iam_role_policy_attachment" "attach_logging_access" { 
  role = aws_iam_role.lambda_role.name 
  policy_arn = aws_iam_policy.lambda_logging.arn 
  }

resource "aws_iam_role_policy_attachment" "attach_parameter_access" { 
  role = aws_iam_role.lambda_role.name 
  policy_arn = aws_iam_policy.lambda_get_parameter.arn 
  }







