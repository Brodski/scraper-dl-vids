# Terrafrom's workspaces is bad for envs
# https://developer.hashicorp.com/terraform/cli/workspaces#when-not-to-use-multiple-workspaces

provider "aws" {
  region = "us-east-1"
  # alias  = "navbar_footer_injector__alias"
}


output "s3_assets_output" {
  value = module.s3_assets
}
