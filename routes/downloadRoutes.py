from flask import Blueprint
from flask import jsonify
import asyncio
# const express = require("express");
# const router = express.Router();
from controllers.downloadController import *
from controllers.scrapey import *
import controllers.directoryController as dirController
# or "import controllers.downloadController"
# --> controllers.downloadController.uploadJsonToS3
# const { getUsers, makeUser, getUser, somethingTime } = require("../controllers/users");
# router.get('/', getUsers);

download_bp = Blueprint('download', __name__)

# @download_bp.route('/channel/<name>')
# async def getVidPaths(name=""):
#     if name == "":
#         return   
#     return await scrapePage(name)

@download_bp.route('/saveTopChannels')
def saveTopChannels_Route():
    return saveTopChannels(None)

@download_bp.route('/getTopChannels')
def getTopChannels_Route():
    return getTopChannels()

@download_bp.route('/getTopChannelsAndSave')
def getTopChannelsAndSave_Route():
    return dirController.getTopChannelsAndSave()

@download_bp.route('/initScrape')
def initScrape_Route():
    return dirController.initScrape()

@download_bp.route('/scrape4HrefAux')
def scrape4HrefAux_Route():
    return scrape4HrefAux()

@download_bp.route('/initScrapeHrefs')
def initScrapeHrefs_Route():
    return dirController.initScrapeHrefs()
