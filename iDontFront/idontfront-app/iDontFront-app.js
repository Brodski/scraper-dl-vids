// const AWS = require('aws-sdk');
const serverless = require('serverless-http');
const express = require('express');
const path = require('path');
// const ejs = require('ejs');
const configs = require("./configs");
const mainRoutes = require('./routes/mainRoutes');
const app = express();

app.set('view engine', 'ejs');
app.set('views', './views') // this line not needed b/c views is by default
app.use(express.static(path.join(__dirname, 'public')));
app.set('views', path.join(__dirname, '/views'));

app.locals.configs = configs

// Body Parser Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use(mainRoutes)

if (process.env.IS_LAMBDA == "true") {
    console.log("YES IS LAMBDA 222!!!" + process.env.IS_LAMBDA)
    module.exports.lambdaHandler = async (event, context) => {
        console.log("event.path=" + event.path)
        event.path = event.path === '' ? '/' : event.path
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


