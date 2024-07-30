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
########################
# powershell variables #
########################
param (
    [Parameter(Mandatory=$true)]
    [string]$env,
    [string]$tag
)
$ErrorActionPreference = 'Stop'
$dateString = Get-Date -Format "yyyy.MM.dd_ss's'"
$tag_name = "official_v2_${env}_${dateString}"
$TF_ENVIRONMENT=$env
echo $tag_name
echo $tag_name
echo $tag_name
echo $tag_name
if ($env -ne "prod" -and $env -ne "dev") {
    Write-Host "The environment must be 'prod' or 'dev'."
    exit
}
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 144262561154.dkr.ecr.us-east-1.amazonaws.com
if (-not $?) {
    Write-Error "Aws login command failed"
    exit 1
}
##################
# Terraform Init #
##################
cd "./terraform-idontfront"
terraform init -reconfigure -backend-config="key=${TF_ENVIRONMENT}/idontfront/terraform.tfstate"

################
# Docker build #
################
if ($PSBoundParameters.ContainsKey('tag')) {
    $tag_name = $tag
} else {
    cd "../idontfront-app"
    docker build --no-cache -t "idontfront:$tag_name" -f Dockerfile_idontfront .
}
###############
# Docker push #
###############
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 144262561154.dkr.ecr.us-east-1.amazonaws.com
docker tag "idontfront:$tag_name" "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"
docker push "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"

###################
# Terraform apply #
###################
cd "../terraform-idontfront"
echo "docker_tag_name=$tag_name"
terraform apply --var-file="vars_${TF_ENVIRONMENT}.tfvars"  -var "docker_tag_name=$tag_name" --auto-approve
echo "docker_tag_name=$tag_name"
cd "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\iDontFront-rework"
# terraform apply --var-file="vars_prod.tfvars"  -var "docker_tag_name=official_v2_2024.02.03_46s" --auto-approve