
$dateString = Get-Date -Format "yyyy.MM.dd_ss's'"
$tag_name = "official_v2_$dateString"

cd "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\iDontFront-rework\idontfront-app"
docker build --no-cache -t "idontfront:$tag_name" -f Dockerfile_idontfront .

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 144262561154.dkr.ecr.us-east-1.amazonaws.com
docker tag "idontfront:$tag_name" "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"
docker push "144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:$tag_name"

cd "../terraform"
terraform apply --var-file="vars_dev.tfvars" -var 'docker_tag_name=$tag_name' --auto-approve
# terraform apply --var-file="vars_dev.tfvars"
