#####################################################
#                                                   #
#     RECALL:                                       # 
#                                                   #
#           $ docker build                          #
#           $ docker push                           #
#           $ git push                              #
#     NEED TO RUN:                                  #
#           $ SSScrapy-rework/docker/build_all_ssscrapy_prod.ps1
#                                                   #
#####################################################
$TF_ENVIRONMENT="prod"

terraform init -reconfigure -backend-config="key=${TF_ENVIRONMENT}/ssscrapey/terraform.tfstate"
terraform apply -var-file="vars_${TF_ENVIRONMENT}.tfvars"  --auto-approve
