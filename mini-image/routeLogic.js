const sharp = require('sharp');
const AWS = require('aws-sdk');

AWS.config.update({region: 'us-east-1'});
const s3 = new AWS.S3();

class RouteLogic {
    
    static async doS3Stuff({image, filename, value}) {
        console.log("doing s3 stuff....");
    }
}

module.exports = RouteLogic;