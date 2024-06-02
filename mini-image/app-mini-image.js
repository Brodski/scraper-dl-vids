const express = require('express');
const app = express();
const router = express.Router();

const Transform = require('./transform');
const compress = require('./routes/api/compress');
const path = require("path");

module.exports = router


const port = 6969;
app.use(express.json()) 
app.get('/', async (req, res) => {
  res.sendFile(path.join(__dirname, './routes/ui/homepage.html'));
})

app.post('/api/compress', async (req, res) => {
  console.log("COMPRESSSSS")
  console.log("COMPRESSSSS")
  console.log("COMPRESSSSS")
  console.log("COMPRESSSSS")
  let {img, format} = await compress(req, res)
  if (img == null) {
    console.log("NONONONO")
    console.log(img)
    console.log(format)
    return res.status(400).json({ message: 'Compression failed: Image is null' });
  }
  // RouteLogic.doS3Stuff(img);
  console.log("YES!!!!!!!!!")
  console.log("YES!!!!!!!!!")
  console.log("YES!!!!!!!!!")
  console.log("YES!!!!!!!!!")
  res.setHeader('Content-Type', `image/${format}`);
  res.send(img);
  return ;
});


app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});


test()


async function test() {
    let url = 'https://static-cdn.jtvnw.net/cf_vods/d1m7jfoe9zdc1j/c81b0ac64a8b2806598c_kaicenat_51072986285_1715485410//thumb/thumb0-0x0.jpg';
    let width = 244;
    let rename = null;
    let body = {width, url, rename};
    let req = { body }
    let {img, format} = await compress(req, null)
    return 
}


