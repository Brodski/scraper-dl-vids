const express = require('express');
const app = express();
const router = express.Router();
const serverless = require('serverless-http');

const Transform = require('./transform');
const compress = require('./routes/api/compress');
const path = require("path");

module.exports = router

console.log("process.env.IS_LAMBDA", process.env.IS_LAMBDA)
const PORT = 6969;
app.use(express.json()) 
app.get('/', async (req, res) => {
  res.sendFile(path.join(__dirname, './routes/ui/homepage.html'));
})

app.post('/api/compress', async (req, res) => {
  let {img, format, filename_new} = await compress(req.body, res)
  if (img == null) {
    return res.status(400).json({ message: 'Compression failed: Image is null' });
  }
  console.log(filename_new)
  res.setHeader('Content-Disposition', `attachment; filename="${filename_new}"`);
  res.setHeader('X-Bski-Filename', `${filename_new}`);
  res.setHeader('Content-Type', `image/${format}`);
  res.send(img);
  return ;
});


if (process.env.IS_LAMBDA == "true") {
  console.log("YES!!!!! process.env.IS_LAMBDA", process.env.IS_LAMBDA)
  module.exports.lambdaHandler = async (event, context) => {
      console.log("event=" + event);
      console.log("event=" + JSON.stringify(event));
      console.log("event.path=" + event.path);
      console.log('event.httpMethod', event.httpMethod)
      console.log('event.body', event.body)
      
      let body = !event.isBase64Encoded ? JSON.parse(event.body) : JSON.parse(Buffer.from(event.body, 'base64').toString('utf-8'));
      console.log('body', body)
      if (event.path == "/api/compress" && event.httpMethod == "POST") {
        let {img, format, filename_new} = await compress(body)
        let res = {
            statusCode: 200,
            headers: {
                'Content-Type': `image/${format}`,
                'Content-Disposition': `attachment; filename="${filename_new}"`,
                'X-Bski-Filename': `${filename_new}`,
                'Content-Type': `image/${format}`,
            },
            body: img.toString('base64'),
            isBase64Encoded: true,
        };
        console.log("res is:", res);
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
  app.listen(PORT, () => console.log(`Server running on port http://localhost:${PORT}`));
  // test()
}





async function test() {
    // let url = 'https://static-cdn.jtvnw.net/cf_vods/d1m7jfoe9zdc1j/c81b0ac64a8b2806598c_kaicenat_51072986285_1715485410//thumb/thumb0-0x0.jpg';
    let width = 244;
    let rename = null;
    let body = {width, url, rename};
    let req = { body }
    let {img, format, filename_new} = await compress(req, null)
    return 
}


