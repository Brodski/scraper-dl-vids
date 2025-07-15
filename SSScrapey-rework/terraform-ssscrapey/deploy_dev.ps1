#####################################################
#                                                   #
#     RECALL:                                       # 
#                                                   #
#           $ docker build                          #
#           $ docker push                           #
#           $ git push                              #
#                                                   #
#####################################################
#
# 
# NEED TO RUN
# $ build_all_ssscrapy_dev.ps1
$TF_ENVIRONMENT="dev"

echo "Don't forget to run build_all_ssscrapy_dev.ps1"
terraform init -reconfigure -backend-config="key=${TF_ENVIRONMENT}/ssscrapey/terraform.tfstate"
terraform apply -var-file="vars_${TF_ENVIRONMENT}.tfvars"  --auto-approve
