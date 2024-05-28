const configs = require("../configs");
const databaseSingleton = require("./helpers/DatabaseSingleton");
const path = require("path");
const fs = require("fs");

const imagePath = path.join(process.cwd(), 'public/imgs/favicon.ico');
const imageBytes = fs.readFileSync(imagePath);
const base64Image = imageBytes.toString('base64');
exports.favicon = async (req, res) => {
    res.writeHead(200, {
        'Content-Type': 'image/x-icon',
        'Content-Length': imageBytes.length
    });
    res.end(imageBytes);
    return
}