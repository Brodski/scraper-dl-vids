// export { function1, function2 };

const { env } = require('process');

function fn1() {
    return 'fn1'
} 
function fn2() { 
    console.log('fn2')
    return 'fn2'
}



    // List all of the buckets in your account
    // s3.listBuckets((err, data) => {
    //     if (err) {
    //         console.error(err);
    //     } else {
    //         console.log(data.Buckets);
    //     }
    // });
    
// https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/S3.html#listObjectsV2-property
// good use of nexttoken: https://www.tabnine.com/code/javascript/functions/aws-sdk/ListObjectsV2Output/NextContinuationToken


    // Prefix top1/
    // Delimiter /xxx
    // CommonPrefixes:??, [ { 
        // Prefix: 'top1/sublevel0-c/sublevel1-c-A/xxx' 
    // } ]

    // Prefix top1/
    // Delimiter /
    // CommonPrefixes:??, [
    //     { Prefix: 'top1/sublevel0-b/' },
    //     { Prefix: 'top1/sublevel0-c/' },
    //     { Prefix: 'top1/sublevel0/' }
    // ]

    // Prefix: '',
    // Delimiter: '/',
    // CommonPrefixes: [
    //   { Prefix: 'OriginalVids/' },
    //   { Prefix: 'sample-vids/' },
    //   { Prefix: 'top1/' },
    //   { Prefix: 'vids/' }
    // ],
    
// await function listBuckets() {
        
//     })
// }

const AWS = require('aws-sdk');
// Set your AWS credentials and region
AWS.config.update({
    accessKeyId: env.AWS_ACCESS_KEY, // xxxxxxxxxxxxxxxxxxxxxxxxx
    secretAccessKey: env.AWS_SECRET_ACCESS_KEY, //  xxxxxxxxxxxxxxxxxxxxxxxxxx
    region: env.AWS_BUCKET_REGION // us-east-1
});



async function listBuckets(listRecr = [], token, prefixListRecr=[]) {
    return new Promise((resolve, reject) => {
        // List all of the buckets in your account


        // Create an S3 client
        const s3 = new AWS.S3();
        var bucketParams = {
            Bucket : 'bucket-bski-audio',
            // MaxKeys : 10
            Prefix: '',
            Delimiter: '/',
            // Prefix: self.prefix,
            ContinuationToken: token
        };
        
        // Call S3 to retrieve the list of objects in the bucket
        s3.listObjectsV2(bucketParams, function(err, data) {
            if (err) {
                console.log("Error", err);
                reject("Error", err);
            } else {
                console.log("Success", data);
                console.log("-----------------------------------");
                console.log("-----------------------------------");
                console.log("-----------------------------------");
                console.log(" IsTruncated??,",  data.IsTruncated);
                console.log(" KeyCount??,",  data.KeyCount);
                console.log(" ContinuationToken??,",  data.ContinuationToken);
                console.log(" NextContinuationToken??,",  data.NextContinuationToken);
                console.log(" Prefix??,",  data.Prefix);
                console.log(" StartAfter??,",  data.StartAfter);
                console.log(" CommonPrefixes:??,",  data.CommonPrefixes);

                data.CommonPrefixes.forEach(function (prefixes) {
                    prefixListRecr.push(prefixes.Prefix);
                });
                
                allKeys =[]
                data.Contents.forEach(function (content) {
                    allKeys.push(content.Key);
                });
                listRecr = listRecr.concat(data.Contents);
                if (data.IsTruncated){
                    console.log("go again... listRecr=", listRecr)
                    return listBuckets(listRecr, data.NextContinuationToken, prefixListRecr);
                } 
                else {
                    console.log("listRecr=", {listRecr, prefixListRecr})
                    // return listRecr;
                    // return { listRecr, prefixListRecr};
                    resolve( { listRecr, prefixListRecr});
                }
            }
        });
    })
}


async function maxJsonifyContent(currentPrefix = '', prefixListRecr=[]) {
    return new Promise((resolve, reject) => {

        // Create an S3 client
        const s3 = new AWS.S3();

        var bucketParams = {
            Bucket : 'bucket-bski-audio',
            Prefix: currentPrefix,
            Delimiter: '/',
            ContinuationToken: null // token
        };
        
        s3.listObjectsV2(bucketParams, function(err, data) {
            if (err) {
                console.log("Error", err);
                reject("Error", err);
            } else {
                console.log("Success", data);
                console.log("-----------------------------------");
                console.log("-----------------------------------");
                console.log("-----------------------------------");
                console.log(" currentPrefix,", currentPrefix);
                console.log(" IsTruncated??,",  data.IsTruncated);
                console.log(" NextContinuationToken??,",  data.NextContinuationToken);
                console.log(" Prefix??,",  data.Prefix);
                console.log(" CommonPrefixes:??,",  data.CommonPrefixes);

                data.CommonPrefixes.forEach(function (prefixes) {
                    let x = {
                        "parent": prefixes.Prefix,
                        "children": data.CommonPrefixes,
                    }
                    prefixListRecr.push(prefixes.Prefix);
                    console.log("data.CommonPrefixes.length=",data.CommonPrefixes.length)
                    resolve("DONE")
                    // maxJsonifyContent(prefixes.Prefix, )
                });
                
                // listRecr = listRecr.concat(data.Contents);
                // if (prefixes.length == 0) {
                //     console.log("listRecr=", {listRecr, prefixListRecr})
                //     resolve( { listRecr, prefixListRecr});
                // }
            }
        });
    })
}









function uploadToS3() {
    // Upload a file to S3
    // const fs = require('fs');

    // const fileStream = fs.createReadStream('/path/to/local/file.txt');

    // const params = {
    //   Bucket: 'YOUR_BUCKET_NAME',
    //   Key: 'file.txt',
    //   Body: fileStream
    // };

    // s3.upload(params, (err, data) => {
    //   if (err) {
    //     console.error(err);
    //   } else {
    //     console.log(data);
    //   }
    // });

}
module.exports = {
    fn1,
    fn2,
    listBuckets,
    maxJsonifyContent,
}