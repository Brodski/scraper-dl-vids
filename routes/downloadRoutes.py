from flask import Blueprint
from flask import jsonify
import asyncio
# const express = require("express");
# const router = express.Router();
# from controllers.downloadController import *
from controllers.scrapey import *
import controllers.directoryController as dirController
import controllers.directoryController as downloadController
import controllers.yt_download as ytdl
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
    return downloadController.saveTopChannels(None)

@download_bp.route('/getTopChannels')
def getTopChannels_Route():
    return downloadController.getTopChannels()

@download_bp.route('/getTopChannelsAndSave')
def getTopChannelsAndSave_Route():
    return dirController.getTopChannelsAndSave()

@download_bp.route('/initScrape')
def initScrape_Route():
    return dirController.initScrape()

@download_bp.route('/scrape4HrefAux')
def scrape4HrefAux_Route():
    return scrape4HrefAux()

@download_bp.route('/initYtdlAudio')
def initYtdlAudio_Route():
    return dirController.initYtdlAudio()

@download_bp.route('/getAlreadyDownloaded')
def getAlreadyDownloaded_Route():
    return dirController.getAlreadyDownloadedxx()

@download_bp.route('/downloadTwtvVid_FIXED')
def downloadTwtvVid_FIXED_Route():
    return ytdl.downloadTwtvVid("/videos/5057810")
    # return ytdl.downloadTwtvVid("/videos/28138895")
