
const https = require('https');
const Transform = require('../../transform');


const MAX_SIZE = 1024 * 1024 * 5; // 5 MB size limit

async function compress(body) {
    const { imageUrl, width, percent } = { "imageUrl": body?.imageUrl, "width": body?.width, "percent": body?.percent };
    let buffImage = null;

    try {
        buffImage = await downloadImage(imageUrl);
    } catch (error) {
        console.error("error", error)
        return {"img": null, "format": null, "filename_new": null}
    }
    
    let filename = extractNameFromUrl(imageUrl);
    let val = width ? width : percent

    let {img, format, filename_new} = await Transform.reduceImg({"image": buffImage, "filename": filename, "value": Number(val)});
    console.log(img)
    console.log(format)
    
    return {img, format, filename_new}
}

// www.bigboy.com/image/of/bigboy =>  bigboy.jpg
function extractNameFromUrl(url) {
    try {
        console.log("    (Extract) url: ", url)
        let filenameDefault = null;
        let lastIdxDot = url.lastIndexOf(".");
        let lastIdxSlash = url.lastIndexOf("/");

        // Ends in a file type eg www.bigboy.com/image/of/bigboy.jpg
        if (lastIdxDot > lastIdxSlash) {
            let lastIdxJunkBefore = url.slice(0, lastIdxDot).lastIndexOf("/");
            filenameDefault = url.slice(lastIdxJunkBefore + 1, lastIdxDot);
        }
        else if (lastIdxDot > lastIdxSlash) { // else www.bigboy.com/image/of/bigboy
            filenameDefault = url.slice(lastIdxSlash + 1);
        }

        filenameDefault = filenameDefault.replace(/[^a-zA-Z0-9]/g, '');
        filenameDefault = filenameDefault.replace(/(0x0|00x0)$/, '');
        filenameDefault = filenameDefault == "" ? "imagefile" : filenameDefault;
        filenameDefault = filenameDefault.substring(0, 20);
        return filenameDefault;
    } catch (e) {
        console.log("oops");
        console.error(e);
        return "imagefile";
    }
}

function downloadImage(url) {
  return new Promise((resolve, reject) => {
    const request = https.get(url, response => {
        console.log(`Attempting to download image from URL: ${url}`);

        const chunks = [];
        let downloadedSize = 0;

        response.on('data', chunk => {
            downloadedSize += chunk.length;
            chunks.push(chunk);
            
            // Check if the downloaded size exceeds the maximum allowed size
            if (downloadedSize > MAX_SIZE) {
                request.abort();
                reject(new Error('File size exceeds the limit'));
            }
        });

        response.on('end', () => {
            if (response.statusCode === 200) {
                const buffer = Buffer.concat(chunks);
                resolve(buffer);
            } else {
                reject(new Error(`Request failed with status code: ${response.statusCode}`));
            }
        });
    });

    request.on('error', err => {
      reject(err);
    });

    request.on('abort', () => {
      reject(new Error('Request aborted due to size limit'));
    });
  });
}

module.exports = compress;