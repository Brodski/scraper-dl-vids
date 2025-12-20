#####################################################
#                                                   #
#     RECALL:                                       # 
#                                                   #
#           $ docker build                          #
#           $ docker push                           #
#           $ git push                              #
#     NEED TO RUN:                                  #
#     NEED TO RUN:                                  #
#     NEED TO RUN:                                  #
#     NEED TO RUN:                                  #
#           $ SSScrapy-rework/docker/build_all_ssscrapy_dev.ps1
#                ⬆️                                 #
#                ⬆️                                 #
#                ⬆️                                 #
#                ⬆️                                 #
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
#  --log-group-name "/your/log/group" \             /scraper/vastai_master/dev
#  --log-stream-name "your-log-stream" \            "2025/12/01/dev_vastai_master[$LATEST]bf814868a6c144789a94005820bbe5ea"
#  --output text > logs.txt
#  --region us-east-1

# aws logs get-log-events   --log-group-name "/scraper/vastai_master/dev"  --log-stream-name "2025/12/01/dev_vastai_master[$LATEST]bf814868a6c144789a94005820bbe5ea"  --region us-east-1  --output text > logs.txt