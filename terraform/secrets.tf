
resource "aws_secretsmanager_secret" "api_credentials" {
  name = "api_credentials"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "api_credentials" {
  secret_id     = aws_secretsmanager_secret.api_credentials.id
  secret_string = data.local_sensitive_file.api_credentials.content
}

data "local_sensitive_file" "api_credentials" {
  filename = "${path.module}/../api_credentials.json"
}

data "aws_secretsmanager_secret_version" "api_credentials"{
  secret_id = aws_secretsmanager_secret.api_credentials.id
  depends_on = [aws_secretsmanager_secret_version.api_credentials ]
}

locals {
  api_credentials= jsondecode(data.aws_secretsmanager_secret_version.api_credentials.secret_string)
}

