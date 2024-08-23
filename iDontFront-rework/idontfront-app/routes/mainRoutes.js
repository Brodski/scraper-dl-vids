const express = require('express');
const router = express.Router();
const cRobots = require("../controllers/robots");
const cSitemap = require("../controllers/sitemap");
const cHome = require("../controllers/home");
const cFavicon = require("../controllers/favicon");
const routeHelper = require("./routeHelper");

router.get(["/favicon.ico"], cFavicon.favicon);
router.get(["/", "/index"], cHome.homepage);
router.get(["/robots.txt"], cRobots.robots);
router.get(["/sitemap.xml"], cSitemap.sitemap);
router.get(["/channel/:name", 
            "/channel/:name/btest", 
            "/channel/:name/:id", 
            "/channel/:name/:id/analysis", 
            "/channel/:name/:id/wordtree"], 
            routeHelper.routeHelper);


router.get('*', async (req, res) => {
    res.status(404)
    res.render("../views/404", {})
});
module.exports = { "mainRoutes": router }