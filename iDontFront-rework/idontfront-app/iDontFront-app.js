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
if (process.env.NODE_ENV == "prod") {
    require('dotenv').config({ path: './.env_prod' });
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


console.log("DATABASE_HOST=", process.env.DATABASE_HOST)
console.log("DATABASE_USERNAME=", process.env.DATABASE_USERNAME)
console.log("DATABASE=", process.env.DATABASE)
console.log("BUCKET_DOMAIN=", process.env.BUCKET_DOMAIN)


// process.env.LD_LIBRARY_PATH = process.env.LAMBDA_TASK_ROOT + "/lib"
if (process.env.IS_LAMBDA == "true") {
    module.exports.lambdaHandler = async (event, context) => {
        console.log("event.path=" + event.path);
        event.path = event.path === '' ? '/' : event.path

        context.callbackWaitsForEmptyEventLoop = false;
        const serverlessHandler = serverless(app)
        const result = await serverlessHandler(event, context)
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