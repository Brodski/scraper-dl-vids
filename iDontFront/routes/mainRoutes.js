const express = require('express');
const router = express.Router();
const controller = require("../controllers/home");

// require("dotenv").config();

router.get(["/", "/420"], controller.get_vod_by_id);

module.exports = router