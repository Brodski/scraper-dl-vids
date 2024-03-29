const express = require('express');
const router = express.Router();
const cHome = require("../controllers/home");
const cChannel = require("../controllers/channel");


router.get(["/", "/index"], cHome.homepage);
router.get(["/channel/:name", 
            "/channel/:name/:id", 
            "/channel/:name/:id/analysis", 
            "/channel/:name/:id/wordtree"], 
        cChannel.channel);
// router.get("/channel/:name/:id", cVod.vod);

module.exports = router