const express = require('express');
const fs = require('fs');
const path = require('path');
const serverless = require('serverless-http');

console.log("process.env.NODE_ENV: ", process.env.NODE_ENV)
console.log("process.env.ENV: ", process.env.ENV)
console.log("process.env.LAMBDA_ENV: ", process.env.LAMBDA_ENV)
if (process.env.NODE_ENV == "local") {
    require('dotenv').config(); // reads .env by default
} 


const app = express();
const configs = require("./configs");
const mainRoutes = require('./routes/mainRoutes');
app.set('view engine', 'ejs');
app.set('views', './views');
app.use(express.static(path.join(__dirname, 'public')));
app.set('views', path.join(__dirname, '/views'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(mainRoutes)
app.locals.configs = configs


// process.env.LD_LIBRARY_PATH = process.env.LAMBDA_TASK_ROOT + "/lib"
if (process.env.IS_LAMBDA == "true") {
    module.exports.lambdaHandler = async (event, context) => {

        const directoryPath = path.join(__dirname);
        fs.readdir(directoryPath, function (err, files) {
            if (err) {
                console.log('Unable to scan directory: ' + err);
            } 
            files.forEach(function (file) {
                console.log(file); 
            });
        });





        console.log("YES IS LAMBDA !!!" + process.env.IS_LAMBDA)        
        console.log("event.path=" + event.path);
        if (process.env.IS_SAM == "true" && event.path.slice(0,4) == "/v1/") {
            event.path = event.path.slice(3)
        }
        console.log("event.path2=" + event.path);
        event.path = event.path === '' ? '/' : event.path

        context.callbackWaitsForEmptyEventLoop = false;
        const serverlessHandler = serverless(app)
        const result = await serverlessHandler(event, context)
        console.log("result")
        console.log(result)
        return result
    }
}
else {
    const PORT = process.env.PORT || 3333;
    app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
}


function doDebug() {
    const directoryPath = process.cwd();
    fs.readdir(directoryPath, { withFileTypes: true }, (err, files) => {
        if (err) {
            return console.log('Unable to scan directory: ' + err);
        } 
        files.forEach(file => {
            if (file.isDirectory()) {
            console.log(`DIR: ${file.name}`);
            } else {
            console.log(`FILE: ${file.name}`);
            }
        });
    });
}