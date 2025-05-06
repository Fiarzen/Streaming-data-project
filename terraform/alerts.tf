
resource "aws_sns_topic" "lambda_alerts" {
    name = "lambda_alerts"
}

resource "aws_cloudwatch_metric_alarm" "lambda_alarm" {
  alarm_name                = "lambda_alarm"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 2
  metric_name               = "Errors"
  namespace                 = "AWS/Lambda"
  period                    = 120
  statistic                 = "Sum"
  threshold                 = 1
  alarm_description         = "This metric monitors lambda errors"
  insufficient_data_actions = []
  alarm_actions = [aws_sns_topic.lambda_alerts.arn]
}

