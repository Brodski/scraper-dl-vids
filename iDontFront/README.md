cd terraform  
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
npm i puppeteer  
  
  
  
added to context.js and plot.js --->
import { JSDOM } from "jsdom";
const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');


file: d3-selection/src/create.js  
import { JSDOM } from "jsdom";  
const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');  
  
export default function(name) {  
  let document = dom.window.document;  
  return select(creator(name).call(document.documentElement));  
}  
