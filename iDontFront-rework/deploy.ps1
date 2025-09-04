####################################################
#                                                  #
#                   HOW TO DEPLOY                  #
#                                                  #
####################################################
# $ ./deploy.ps1 -env "dev"
# $ ./deploy.ps1 -env "dev" -tag "official_v2_dev_2024.04.10_33s"
# $ ./deploy.ps1 -env "prod" -tag "official_v2_prod_2024.04.12_30s"


####################################################
#                                                  #
#                    SCRIPT                        #
#                                                  #
####################################################
##########
# Set up #
##########
param (
    [Parameter(Mandatory=$true)]
    [string]$env
)
$ErrorActionPreference = 'Stop'

########################
# powershell variables #
########################
$dateString     = Get-Date -Format "yyyy.MM.dd_ss's'"
$tag_name       = "official_v2_${env}_${dateString}"
$TF_ENVIRONMENT = $env
if ($env -ne "prod" -and $env -ne "dev") {
    Write-Host "The environment must be 'prod' or 'dev'."
    exit
}

#########
# Login #
#########
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 144262561154.dkr.ecr.us-east-1.amazonaws.com

##################
# Terraform Init #
##################
cd "./terraform-idontfront"
terraform init -reconfigure -backend-config="key=${TF_ENVIRONMENT}/idontfront/terraform.tfstate"

################
# Docker build #
################
cd "../idontfront-app"
docker build --no-cache -t "idontfront:$tag_name" -f Dockerfile_idontfront .

###############
# Docker push #
###############
echo "cd './terraform-idontfront'"
echo "terraform init -reconfigure -backend-config='key=${TF_ENVIRONMENT}/idontfront/terraform.tfstate'"
echo "cd '../idontfront-app'"
echo "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 144262561154.dkr.ecr.us-east-1.amazonaws.com"
echo "docker tag idontfront:$tag_name 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"
echo "docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"
echo "cd '../terraform-idontfront'"
echo "terraform apply --var-file='vars_${TF_ENVIRONMENT}.tfvars'  -var 'docker_tag_name=$tag_name' --auto-approve"
echo "docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"


aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 144262561154.dkr.ecr.us-east-1.amazonaws.com 
docker tag "idontfront:$tag_name" "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"
docker push "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"

###################
# Terraform apply #
###################
cd "../terraform-idontfront"
terraform apply --var-file="vars_${TF_ENVIRONMENT}.tfvars"  -var "docker_tag_name=$tag_name" --auto-approve
