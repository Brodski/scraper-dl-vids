const express = require('express');
const app = express();
const fs = require('fs');
const path = require('path');
const serverless = require('serverless-http');
const minifyHTML = require('express-minify-html-terser');

const { mainRoutes } = require('./routes/mainRoutes');

if (process.env.NODE_ENV == "local") {
    require('dotenv').config(); // reads .env by default
} 
if (process.env.NODE_ENV == "prod") {
    require('dotenv').config({ path: './.env_prod_local_test' });
}

app.use(minifyHTML({
    override: true,
    exception_url: [
        '/sitemap.xml',                        // A specific URL
        // /\/api\/.*/,                     // A regex to exclude API routes
        // function(req, res) {             // A function for custom logic
        //     return req.path === '/skip'; // Skip minification for '/skip' route
        // }
    ],
    htmlMinifier: {
      collapseWhitespace: true,
      removeComments: true,
      minifyCSS: false,
      minifyJS: false
    }
  }));

app.use((req, res, next) => {
    res.set('Cache-Control', 'stale-while-revalidate=300, stale-if-error=86400'); // https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
next();
});
app.set('view engine', 'ejs');
app.set('views', './views');
app.use(express.static(path.join(__dirname, 'public')));
app.set('views', path.join(__dirname, '/views'));
app.use(express.json());
app.use(mainRoutes)
  
console.log("DATABASE_HOST=", process.env.DATABASE_HOST)
console.log("DATABASE_USERNAME=", process.env.DATABASE_USERNAME)
console.log("DATABASE=", process.env.DATABASE)
console.log("BUCKET_DOMAIN=", process.env.BUCKET_DOMAIN)

// process.env.LD_LIBRARY_PATH = process.env.LAMBDA_TASK_ROOT + "/lib"


// doDebug();

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

if (process.env.IS_LAMBDA == "true") {
    const img_exts = new Set([".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp"]);
    module.exports.lambdaHandler = async (event, context) => {
        console.log("event.path=" + event.path);
        if (img_exts.has(event.path.slice(event.path.lastIndexOf('.')))) {
            let res = route_img2(event);
            // await sleep(2000);
            return res;
        }
        event.path = event.path === '' ? '/' : event.path
        context.callbackWaitsForEmptyEventLoop = false;
        const serverlessHandler = serverless(app)
        const result = await serverlessHandler(event, context)
        return result
    }
}
else {
    const PORT = process.env.PORT || 3334;
    app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
}

function route_img2(event) {
    event.path = event.path == "/favicon.ico" ? "/imgs/favicon.ico" : event.path;
    const decodedPath = decodeURIComponent(event.path);
    let ext = path.extname(decodedPath);
    const mimeType = getMimeType(ext);

    try {
        const imagePath = path.join(__dirname, "public/" + decodedPath);
        const imageBytes = fs.readFileSync(imagePath);
        const base64Image = imageBytes.toString('base64');

        return {
            statusCode: 200,
            headers: {
                'Content-Type': mimeType,
            },
            body: base64Image,
            isBase64Encoded: true,
        };
    }
    catch (e) {
        console.log("nope", e)
        return {
            statusCode: 404,
            headers: {
            'Content-Type': `image/png`,
            },
            body: "",
            isBase64Encoded: true,
        };
    }
}
function getMimeType(ext) {
    const mimeTypes = {
        '.ico': 'image/x-icon',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
    };

    return mimeTypes[ext.toLowerCase()] || 'application/octet-stream';
}


function doDebug(coolPath) {
    const directoryPath = coolPath ? coolPath : process.cwd();

    console.log(directoryPath)
    if (directoryPath.includes("node_modules")
        || directoryPath.includes("canvas")
        || directoryPath.includes("build")
    ) {
        return
    }

    fs.readdir(directoryPath, { withFileTypes: true }, (err, files) => {
        if (err) {
            return console.log('Unable to scan directory: ' + err);
        } 
        files.forEach(file => {
            const itemPath = path.join(directoryPath, file.name);
            if (file.isDirectory()) {
                console.log(`DIR: ${itemPath}`);
                doDebug(itemPath)
            } else {
                console.log(`FILE: ${itemPath}`);
            }
        });
    });
}
