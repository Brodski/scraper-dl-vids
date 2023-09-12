# Terrafrom's workspaces is bad for envs
# https://developer.hashicorp.com/terraform/cli/workspaces#when-not-to-use-multiple-workspaces

provider "aws" {
  region = "us-east-1"
  # alias  = "navbar_footer_injector__alias"
}
# terraform {
#   backend "s3" {
#     bucket = "dev-dev-dev-my-terraform-state-bucket-money"
#     key    = "path/dev/state.tfstate"
#     region = "us-east-1"
#   }
# }

module "s3_assets" {
  source      = "./s3-assets"
  s3_asset_bucket_name     = var.s3_asset_bucket_name
  s3_log_bucket_name       = var.s3_log_bucket_name
  s3_log_bucket_resource     = aws_s3_bucket.log_bucket.bucket

  r53_s3_asset_full_domain = var.r53_s3_asset_full_domain
  r53_acm_certificate_arn  = var.r53_acm_certificate_arn
  r53_route_id             = var.r53_route_id
}

output "s3_assets_output" {
  value = module.s3_assets
}

output "log_bucket" {
  value = "${aws_s3_bucket.log_bucket.bucket_domain_name}"
}

