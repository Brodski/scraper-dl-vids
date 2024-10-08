#####################################################
#                                                   #
#     RECALL:                                       # 
#                                                   #
#           $ docker build                          #
#           $ docker push                           #
#           $ git push                              #
#                                                   #
#####################################################
$TF_ENVIRONMENT="dev"

terraform init -reconfigure -backend-config="key=${TF_ENVIRONMENT}/ssscrapey/terraform.tfstate"
terraform apply -var-file="vars_${TF_ENVIRONMENT}.tfvars"  --auto-approve
