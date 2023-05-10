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


####################################################
# 1
# Make http request to sullygnome. 3rd party website
# Decide who we want to look at
# Saves "who" to S3
@everything_bp.route('/main/ranking/getTopChannelsAndSave')
def getTopChannelsAndSave_Route():
    return mainController.getTopChannelsAndSave()

@ranking_bp.route('/saveTopChannels')
def saveTopChannels_Route():
    return rankingController.saveTopChannels(None)

@ranking_bp.route('/getTopChannels')
def getTopChannels_Route():
    return rankingController.getTopChannels()

####################################################



####################################################
# After 1                                          #
# Retrieves data from our S3 bucket
# S3 bucket already has channel info. post gnome
@everything_bp.route('/main/initScrape/getChannelFromS3')
def initScrape_Route():
    return mainController.getChannelFromS3()

####################################################


# After 2? def after 1
# Downloads audio
@everything_bp.route('/main/ytdl/initYtdlAudio')
def initYtdlAudio_Route():
    return mainController.initYtdlAudio({}, True) # isDebuging = True



@everything_bp.route('/ytdl/test/downloadTwtvVid_FIXED')
def downloadTwtvVid_FIXED_Route():
    return ytdl.downloadTwtvVid("/videos/5057810")
    # return ytdl.downloadTwtvVid("/videos/28138895")

@everything_bp.route('/ytdl/getAlreadyDownloaded')
def getAlreadyDownloaded_Route():
    return ytdl.getAlreadyDownloaded("lolgeranimo")




@everything_bp.route('/hrefGet/scrape4VidHref/mock')
def scrape4VidHref_Route():
    return videoHrefController.scrape4VidHref({}, True)

