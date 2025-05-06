resource "aws_sqs_queue" "guardian_content" {
  name                      = "guardian_content"
  message_retention_seconds = 259200
}
