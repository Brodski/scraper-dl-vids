const express = require('express');
const router = express.Router();
const cHome = require("../controllers/home");
const cChannel = require("../controllers/channel");

// require("dotenv").config();

// router.get(["/get", "/420"], controller.get_vod_by_id);
router.get(["/", "/index"], cHome.homepage);
router.get("/channel/:name", cChannel.channel);

module.exports = router