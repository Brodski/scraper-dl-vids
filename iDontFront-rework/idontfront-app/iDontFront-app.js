const express = require('express');
const fs = require('fs');
const path = require('path');
const serverless = require('serverless-http');

console.log("process.env.NODE_ENV: ", process.env.NODE_ENV)
if (process.env.NODE_ENV == "prod") {
    // require('dotenv').config({ path: './config/myenv.env' });
} else {
    require('dotenv').config();
}


const app = express();
const configs = require("./configs");
const mainRoutes = require('./routes/mainRoutes');


app.set('view engine', 'ejs');
app.set('views', './views') // this line not needed b/c views is by default
app.use(express.static(path.join(__dirname, 'public')));
app.set('views', path.join(__dirname, '/views'));


// Body Parser Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use(mainRoutes)
app.locals.configs = configs


// process.env.LD_LIBRARY_PATH = process.env.LAMBDA_TASK_ROOT + "/lib"
if (process.env.IS_LAMBDA == "true") {
    module.exports.lambdaHandler = async (event, context) => {
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