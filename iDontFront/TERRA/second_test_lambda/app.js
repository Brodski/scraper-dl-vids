exports.lambdaHandler2 = async (event, context) => {
    console.log("YES!!!")
    const httpMethod = event.httpMethod;

    const queryStringParameters = event.queryStringParameters;
    const headers = event.headers;
    const body = event.body;


    console.log("You know it!")
    console.log("You know it!")
    console.log("You know it!")
    console.log("You know it!")
    console.log("You know it!")
    // var count = Object.keys(x).length;
    // console.log(count)
    const html = `
        <html>
            <head>
                <title> SECOND THINGY </title>
            </head>
            <body>
                <h1> SECOND LAMBDA!!!! DEV</h1>
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