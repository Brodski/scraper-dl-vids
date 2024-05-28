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
const mainRoutes = require('./routes/mainRoutes');
app.set('view engine', 'ejs');
app.set('views', './views');
app.use(express.static(path.join(__dirname, 'public')));
app.set('views', path.join(__dirname, '/views'));
app.use(express.json());
// app.use(express.urlencoded({ extended: false }));
app.use(mainRoutes)


console.log("DATABASE_HOST=", process.env.DATABASE_HOST)
console.log("DATABASE_USERNAME=", process.env.DATABASE_USERNAME)
console.log("DATABASE=", process.env.DATABASE)
console.log("BUCKET_DOMAIN=", process.env.BUCKET_DOMAIN)


// process.env.LD_LIBRARY_PATH = process.env.LAMBDA_TASK_ROOT + "/lib"
if (process.env.IS_LAMBDA == "true") {
    module.exports.lambdaHandler = async (event, context) => {
        console.log("event.path=" + event.path);
        
        // if (event.path.startsWith('/favicon.ico') || event.path.startsWith('/imgs/beard2.png')) {
        if (event.path.startsWith('/imgs/beard2.png')) {
            let resp = route_img();
            return resp;
        }


        event.path = event.path === '' ? '/' : event.path
        context.callbackWaitsForEmptyEventLoop = false;
        const serverlessHandler = serverless(app)
        const result = await serverlessHandler(event, context)
        // let contentType = result.headers['content-type'] ?? result.headers['Content-Type'] ;
        // let isString = typeof contentType === 'string';
        // if (isString && contentType.startsWith('image')) {  // 'image/gif', 'image/x-icon', ect 
        //     result.isBase64Encoded = true;
        // }
        return result
    }
}
else {
    const PORT = process.env.PORT || 3333;
    app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
}

function route_favicon() {
}
function route_img() {
    const imagePath = path.join(__dirname, 'public/imgs/beard2.png');
    const imageBytes = fs.readFileSync(imagePath);
    const base64Image = imageBytes.toString('base64');
    return {
        statusCode: 200,
        headers: {
          'Content-Type': 'image/png',
        },
        body: base64Image,
        isBase64Encoded: true,
    };
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