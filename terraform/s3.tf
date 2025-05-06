resource "aws_s3_bucket" "code_bucket" {
  bucket_prefix = "code-bucket"
  tags = {
    Name = "Code Bucket"
  }
  
}

resource "aws_s3_object" "lambda_code" {
  bucket   = aws_s3_bucket.code_bucket.bucket
  key      = "guardian_api_client/function.zip"
  source   = "${path.module}/../packages/guardian_api_client/function.zip"
  etag     = filemd5("${path.module}/../packages/guardian_api_client/function.zip")
}

resource "aws_s3_object" "lambda_layer" {
  bucket = aws_s3_bucket.code_bucket.bucket
  key    = "layer/ingestion_layer.zip"
  source = data.archive_file.layer_code.output_path
  etag   = filemd5(data.archive_file.layer_code.output_path)
  depends_on = [ data.archive_file.layer_code ]
}
