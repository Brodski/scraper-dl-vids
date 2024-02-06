$TF_ENVIRONMENT="dev"

terraform init -reconfigure -backend-config="key=${TF_ENVIRONMENT}/ssscrapey/terraform.tfstate"
terraform apply -var-file="vars_${TF_ENVIRONMENT}.tfvars"  --auto-approve

#terraform apply -var-file="vars_${TF_ENVIRONMENT}.tfvars"  -backend-config="key=${TF_ENVIRONMENT}/ssscrapey/terraform.tfstate"
# terraform init -backend-config="key=${TF_ENVIRONMENT}/ssscrapey/terraform.tfstate"