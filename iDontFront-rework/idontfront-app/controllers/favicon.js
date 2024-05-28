const path = require("path");
const fs = require("fs");
//
// Note: Binary media types must be configured at api-gateway / terraform 
//
const imagePath = path.join(process.cwd(), 'public/imgs/favicon.ico');
const imageBytes = fs.readFileSync(imagePath);
const base64Image = imageBytes.toString('base64');
exports.favicon = async (req, res) => {
    console.log("favicon wtf")
    // console.log(base64Image)
    res.writeHead(200, {
        'Content-Type': 'image/x-icon',
        'Content-Encoding': 'base64'
    });
    res.base64Image = true
    res.isBase64Encoded = true
    console.log("res")
    console.log(res)
    // res.end(imageBytes);
    res.end(base64Image);
    return
}