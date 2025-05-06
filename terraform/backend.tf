#specifies s3 bucket to save tfstate to

terraform {
  backend "s3" {
    bucket                   = "tf-state-bucket-2025-jeremy-de-streaming-data-project"
    key                      = "jeremy-streaming-data-project"
    region                   = "eu-west-2"
    shared_credentials_files = ["~/.aws/credentials"]
  }
}

provider "aws" {
  region                   = var.region
  shared_credentials_files = ["~/.aws/credentials"]
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}