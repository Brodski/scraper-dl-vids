const https = require('https');
const Transform = require('./transform');
const RouteLogic = require('./routeLogic');
const sharp = require('sharp');

const MAX_SIZE = 1024 * 1024 * 5; // 5 MB size limit


const express = require('express');
const app = express();
const port = 6969;

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});

app.get('/compress', async (req, res) => {
    const query = req.query;
    console.log("query", query)
    // // res.send('Hello, World!');
    // res.json({
    //     message: 'Query parameters received',
    //     query: query,
    //   });

    let image = './imgs/thumb.jpg'
    let width = 222;
    let optionzWidth = {"image": image, "filename": "mini-compress-img", "width": width};
    let {img, format} = await Transform.reduceToPixels(optionzWidth);
    RouteLogic.doS3Stuff(img);
    res.setHeader('Content-Type', `image/${format}`);
    res.send(img);
});


main()


async function main() {
    // let buffImage = downloadImage('https://example.com/path/to/image.jpg');
    let width = 200;
    let percent = 0.35;
    let filename = "smaller-imageX"

    let url = 'https://static-cdn.jtvnw.net/cf_vods/d1m7jfoe9zdc1j/c81b0ac64a8b2806598c_kaicenat_51072986285_1715485410//thumb/thumb0-0x0.jpg';
    let buffImage = await downloadImage(url);
    filename = filename ? filename : getDefaultFilename(url);

    let optionzWidth = {"image": buffImage, "filename": filename, "width": width};
    let optionzPercent = {"image": buffImage, "filename": filename, "percent": width};
    await Transform.reduceToPixels(optionzWidth);
    // await Transform.halfItWithmeta(optionz)
}

function getDefaultFilename(url) {
    let lastIdx = url.lastIndexOf(".");
    let extension = url.slice(lastIdx); // .jpg
    let lastIdx2 = url.slice(0, lastIdx).lastIndexOf("/");
    let filenameDefault = url.slice(lastIdx2 + 1, lastIdx);
    console.log("filenameDefault", filenameDefault)
    return filenameDefault;

}

function downloadImage(url) {
  return new Promise((resolve, reject) => {
    const request = https.get(url, response => {

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

