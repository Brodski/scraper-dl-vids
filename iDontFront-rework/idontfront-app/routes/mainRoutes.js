const express = require('express');
const router = express.Router();
const cHome = require("../controllers/home");
const cFavicon = require("../controllers/favicon");
const routeHelper = require("./routeHelper");

// router.get(["/favicon.ico"], cFavicon.favicon);
router.get(["/", "/index"], cHome.homepage);
router.get(["/channel/:name", 
            "/channel/:name/btest", 
            "/channel/:name/:id", 
            "/channel/:name/:id/analysis", 
            "/channel/:name/:id/wordtree"], 
            routeHelper.routeHelper);
// router.get("/channel/:name/:id", cVod.vod);

module.exports = router