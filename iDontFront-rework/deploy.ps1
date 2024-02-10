
# $ ./deploy.ps1 -env "dev"
# $ ./deploy.ps1 -env "dev" -tag "offical_v2_123123123"
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

if ($env -ne "prod" -and $env -ne "dev") {
    Write-Host "The environment must be 'prod' or 'dev'."
    exit
}
Write-Host "The environment is $tag_name"
Write-Host "The environment is $tag_name"
Write-Host "The environment is $tag_name"
Write-Host "The tag is $tag"
Write-Host "The tag is $tag"
Write-Host "The tag is $tag"
Write-Host "The tag is $tag"
Write-Host "The tag is $tag"
# if ($tag -ne $null) {
if ($PSBoundParameters.ContainsKey('tag')) {
    Write-Host "The TAG is NULL"
    $tag_name = $tag
} else {
    Write-Host "The TAG is NOT NULL"
    Write-Host "The TAG is NOT NULL"
    Write-Host "The TAG is NOT NULL"
    Write-Host "The TAG is NOT NULL"
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