from flask import Blueprint
from flask import jsonify
# import asyncio
# const express = require("express");
# const router = express.Router();
# from controllers.downloadController import *
# from controllers.scrapey import *
import controllers.videoHrefController as videoHrefController
import controllers.mainController as mainController
import controllers.rankingController as rankingController
import controllers.yt_download as ytdl
# or "import controllers.downloadController"
# --> controllers.downloadController.uploadJsonToS3

#variable is used in app.py
everything_bp = Blueprint('download', __name__)
ranking_bp = Blueprint('ranking', __name__)



@ranking_bp.route('/saveTopChannels')
def saveTopChannels_Route():
    return rankingController.saveTopChannels(None)

@ranking_bp.route('/getTopChannels')
def getTopChannels_Route():
    return rankingController.getTopChannels()




@everything_bp.route('/getTopChannelsAndSave')
def getTopChannelsAndSave_Route():
    return mainController.getTopChannelsAndSave()

@everything_bp.route('/initScrape')
def initScrape_Route():
    return mainController.initScrape()

@everything_bp.route('/initYtdlAudio')
def initYtdlAudio_Route():
    return mainController.initYtdlAudio()

@everything_bp.route('/getAlreadyDownloaded')
def getAlreadyDownloaded_Route():
    return mainController.getAlreadyDownloadedxx()




@everything_bp.route('/scrape4VidHrefAux')
def scrape4VidHrefAux_Route():
    return videoHrefController.scrape4VidHrefAux()


@everything_bp.route('/downloadTwtvVid_FIXED')
def downloadTwtvVid_FIXED_Route():
    return ytdl.downloadTwtvVid("/videos/5057810")
    # return ytdl.downloadTwtvVid("/videos/28138895")
