#####################################################
#                                                   #
#     RECALL:                                       # 
#                                                   #
#           $ docker build                          #
#           $ docker push                           #
#           $ git push                              #
#     NEED TO RUN:                                  #
#           $ SSScrapy-rework/docker/build_all_ssscrapy_dev.ps1
#                                                   #
#####################################################
#
# 
$TF_ENVIRONMENT="dev"

echo "Don't forget to run build_all_ssscrapy_dev.ps1"
terraform init -reconfigure -backend-config="key=${TF_ENVIRONMENT}/ssscrapey/terraform.tfstate"
terraform apply -var-file="vars_${TF_ENVIRONMENT}.tfvars"  --auto-approve


#########################
# SICK TIP
# set PYTHONUTF8=1 
# aws logs get-log-events \
#  --log-group-name "/your/log/group" \             /scraper/preper_dev"
#  --log-stream-name "your-log-stream" \            "ecs/dev_preper_container/216d64aa08f0448686cf06b67fee7aac"
#  --output text > logs.txt
