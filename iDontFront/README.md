cd terraform  
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 144262561154.dkr.ecr.us-east-1.amazonaws.com
docker build -t idontfront .
docker tag idontfront:latest 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:latest
docker push 144262561154.dkr.ecr.us-east-1.amazonaws.com/idontfront:latest
terraform apply --var-file="sensitive-vars.tfvars"  
terraform apply --var-file="sensitive-vars.tfvars"  
terraform apply --var-file="sensitive-vars.tfvars"  
terraform apply --var-file="sensitive-vars.tfvars"  
terraform apply --var-file="sensitive-vars.tfvars"  
terraform apply --var-file="sensitive-vars.tfvars"  
terraform apply --var-file="sensitive-vars.tfvars"  
terraform apply --var-file="sensitive-vars.tfvars"  
terraform apply --var-file="sensitive-vars.tfvars"  
terraform apply --var-file="sensitive-vars.tfvars"  

cd idontfront-app   
nodemon iDontFront-app.js   
  
  
npm install jsdom  
npm i @observablehq/plot  
npm i d3  
npm i stopword  
npm i d3-cloud  
npm install canvas  (required by jsondom)  
<!-- npm i puppeteer   -->
  
  
  
added to context.js and plot.js --->
import { JSDOM } from "jsdom";
const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');


file: d3-selection/src/create.js  
import { JSDOM } from "jsdom";  
const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');  

file: d3-clioud/build/d3.layout.cloud.js
const { JSDOM } = require("jsdom");
const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');
let document = dom.window.document;

export default function(name) {  
  let document = dom.window.document;  
  return select(creator(name).call(document.documentElement));  
}  
