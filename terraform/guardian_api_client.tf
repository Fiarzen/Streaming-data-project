data "archive_file" "guardian_api_client" {
  type        = "zip"
  output_path = "${path.module}/../packages/guardian_api_client/function.zip"
  source_dir = "${path.module}/../src/"
}
resource "aws_lambda_function" "guardian_api_client" {
  function_name    = "guardian_api_client"
  source_code_hash = data.archive_file.guardian_api_client.output_base64sha256
  s3_bucket        = aws_s3_bucket.code_bucket.bucket
  s3_key           = "guardian_api_client/function.zip"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = var.default_timeout
  layers           = [aws_lambda_layer_version.dependencies.arn]
  environment {
    variables = {
      SECRETS_ARN = aws_secretsmanager_secret.api_credentials.arn
      GUARDIAN_API_KEY = local.api_credentials["guardian_api_key"]
    }
  }
  depends_on = [aws_s3_object.lambda_code, aws_s3_object.lambda_layer]
}