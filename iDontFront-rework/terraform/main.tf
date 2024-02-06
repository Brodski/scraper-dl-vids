# Terrafrom's workspaces is bad for envs
# https://developer.hashicorp.com/terraform/cli/workspaces#when-not-to-use-multiple-workspaces

provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket = "scraper-transcriptions-terraform-states"
    region = "us-east-1"
    # key set at command line
  }
}