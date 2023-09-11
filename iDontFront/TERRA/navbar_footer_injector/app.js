// const axios = require('axios')
// const url = 'http://checkip.amazonaws.com/';

const getHtml = require('./navbars/reimagine'); 
/**
 *
 * Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
 * @param {Object} event - API Gateway Lambda Proxy Input Format
 *
 * Context doc: https://docs.aws.amazon.com/lambda/latest/dg/nodejs-prog-model-context.html 
 * @param {Object} context
 *
 * Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
 * @returns {Object} object - API Gateway Lambda Proxy Output Format
 * 
 */

exports.lambdaHandler = async (event, context) => {
    console.log("YES!!!")
    const httpMethod = event.httpMethod;

    const queryStringParameters = event.queryStringParameters;
    const headers = event.headers;
    const body = event.body;


    console.log("DEV");
    console.log("DEV");
    console.log("DEV");
    console.log("DEV");
    console.log("DEV");
    console.log("DEV");
    console.log("DEV");
    console.log("DEV");
    console.log("DEV");
    console.log("DEV");
    console.log("DEV");
    console.log("");
    console.log("");
    console.log("httpMethod:", httpMethod);
    console.log("queryStringParameters: %j", queryStringParameters);
    console.log("headers: %j", headers);
    console.log("body: " + body);
    console.log("");
    console.log(queryStringParameters?.language);
    // let x = getHtml(queryStringParameters?.language);
    console.log("x")
    console.log("x")
    console.log("x")
    console.log("x")
    console.log("x")
    // var count = Object.keys(x).length;
    // console.log(count)
    const html = `
        <html>
            <head>
                <title>My HTML Page - DEV</title>
            </head>
            <body>
                <h1>Welcome to my Lambda function! - DEV</h1>
            </body>
        </html>
    `;

    const response = {
        statusCode: 200,
        headers: {
            'Content-Type': 'text/html',
        },
        body: html,
    };

    return response;

};



// response = {
//     'statusCode': 200,
//     'body': JSON.stringify({
//         message: 'hello world, shazam v3 -------------z',
//     })