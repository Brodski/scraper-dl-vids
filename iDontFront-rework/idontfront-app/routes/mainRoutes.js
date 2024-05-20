const express = require('express');
const router = express.Router();
const cHome = require("../controllers/home");
const routeHelper = require("./routeHelper");


router.get(["/", "/index"], cHome.homepage);
router.get(["/channel/:name", 
            "/channel/:name/:id", 
            "/channel/:name/:id/analysis", 
            "/channel/:name/:id/wordtree"], 
            routeHelper.routeHelper);
// router.get("/channel/:name/:id", cVod.vod);

module.exports = router