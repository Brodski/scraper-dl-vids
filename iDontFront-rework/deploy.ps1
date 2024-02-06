

param (
    [Parameter(Mandatory=$true)]
    [string]$env,
    [string]$tag
)


$ErrorActionPreference = 'Stop'
cd "./terraform"
$dateString = Get-Date -Format "yyyy.MM.dd_ss's'"
$tag_name = "official_v2_$dateString"
$TF_ENVIRONMENT=$env

# Init
terraform init -reconfigure -backend-config="key=${TF_ENVIRONMENT}/idontfront/terraform.tfstate"

if ($tag -ne $null) {
# if ($tag -eq $null) {
    $tag_name = $tag

} else {
    # Docker build
    cd "../idontfront-app"
    docker build --no-cache -t "idontfront:$tag_name" -f Dockerfile_idontfront .
}

# Docker push
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 144262561154.dkr.ecr.us-east-1.amazonaws.com
docker tag "idontfront:$tag_name" "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"
docker push "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"

# Terraform apply
cd "../terraform"
echo "docker_tag_name=$tag_name"
terraform apply --var-file="vars_${TF_ENVIRONMENT}.tfvars"  -var "docker_tag_name=$tag_name" --auto-approve
echo "docker_tag_name=$tag_name"
cd "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\iDontFront-rework"
# terraform apply --var-file="vars_prod.tfvars"  -var "docker_tag_name=official_v2_2024.02.03_46s" --auto-approve