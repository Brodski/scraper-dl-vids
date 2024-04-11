
<!-- docker build -t idontfront . -->
docker build --no-cache -t idontfront:official_v2 -f Dockerfile_idontfront  .

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 144262561154.dkr.ecr.us-east-1.amazonaws.com
docker tag idontfront:official_v2 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2
docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:official_v2

cd ../terraform  
terraform apply --var-file="vars_dev.tfvars"  
terraform apply --var-file="vars_dev.tfvars"  
terraform apply --var-file="vars_dev.tfvars"    

cd idontfront-app   
nodemon iDontFront-app.js   
  