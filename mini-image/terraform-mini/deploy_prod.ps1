$TF_ENVIRONMENT="prod"

terraform init -reconfigure -backend-config="key=${TF_ENVIRONMENT}/mini_image/terraform.tfstate"
terraform apply --var-file="vars_${TF_ENVIRONMENT}.tfvars" --auto-approve