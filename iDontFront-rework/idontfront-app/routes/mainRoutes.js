const express = require('express');
const router = express.Router();
const cFavicon = require("../controllers/favicon");
const cRobots = require("./robots");
const cSitemap = require("./sitemap");
const cHome = require("./home");
const routeHelper = require("./routeHelper");

router.get(["/favicon.ico"], cFavicon.favicon);
router.get(["/robots.txt"], cRobots.robots);
router.get(["/sitemap.xml"], cSitemap.sitemap);

router.get(["/", "/index"], cHome.homepage);
router.get(["/channel/:name", 
            "/channel/:name/:id", 
            // "/channel/:name/:id/wordtree"], 
            "/channel/:name/:id/analysis",],
            routeHelper.routeHelper);


router.get('*', async (req, res) => {
    res.status(404)
    res.render("../views/404", {})
});
module.exports = { "mainRoutes": router }