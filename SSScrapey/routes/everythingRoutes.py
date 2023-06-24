import json
from flask import Blueprint
from flask import jsonify
# import asyncio
# const express = require("express");
# const router = express.Router();
# from controllers.downloadController import *
# from controllers.scrapey import *
import controllers.seleniumController as seleniumController
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
    return mainController.initYtdlAudio({}, isDebug=True) # isDebuging = True

@everything_bp.route('/main/ytdl/bigBoyChannelDownloader')
def bigBoyChannelDownloader_Route():
    metadata_Ytdl_list = ytdl.bigBoyChannelDownloader(
        [
            {
            "displayname":"LoLGeranimo",
            "language":"English",
            "logo":"https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
            "twitchurl":"https://www.twitch.tv/lolgeranimo",
            "url":"lolgeranimo",
            "links":["/videos/5057810","/videos/28138895"],
            "todos":["/5057810/","//"]
            # "todos":["/5057810/","/28138895/"]
            },
            {
            "displayname":"LCK",
            "language":"English",
            "logo":"https://static-cdn.jtvnw.net/jtv_user_pictures/04b097ac-9a71-409e-b30e-570175b39caf-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
            "twitchurl":"https://www.twitch.tv/lck",
            "url":"lck",
            "links":["/videos/576354726","/videos/1108764940"],
            "todos":[]
            }
        ],
    chnLimit=3, vidDownloadLimit=2
    )
    return json.loads(json.dumps(metadata_Ytdl_list, default=lambda o: o.__dict__))



@everything_bp.route('/ytdl/test/downloadTwtvVid_FIXED')
def downloadTwtvVid_FIXED_Route():
    # x = ytdl.downloadTwtvVid("/videos/5057810")
    x = ytdl.downloadTwtvVid("https://www.youtube.com/watch?v=R4g5jUqatFk")
    return str(x)
    # return str(x)
    # return ytdl.downloadTwtvVid("/videos/28138895")

@everything_bp.route('/ytdl/getAlreadyDownloadedS3_TEST')
def getAlreadyDownloadedS3_Route():
    return ytdl.getAlreadyDownloadedS3_TEST("lolgeranimo", ['/videos/5057810', '/videos/28138895', '/videos/6666666'])




@everything_bp.route('/hrefGet/scrape4VidHref/mock')
def scrape4VidHref_Route():
    return seleniumController.scrape4VidHref({}, True)




@everything_bp.route('/s3/syncAudioFilesUploadJsonS3')
def syncAudioFilesUploadJsonS3_Route():
    return mainController.syncAudioFilesUploadJsonS3()



@everything_bp.route('/s3/syncCaptionsUploadJsonS3')
def syncCaptionsUploadJsonS3_Route():
    return mainController.syncCaptionsUploadJsonS3()

@everything_bp.route('/s3/_getCompletedAudioJsonSuperS3')
def _getCompletedAudioJsonSuperS3_Route():
    return mainController._getCompletedAudioJsonSuperS3(True)


@everything_bp.route('/s3/_getAllCompletedJsonSuperS3__BETTER')
def _getAllCompletedJsonSuperS3__BETTER_Route():
    return mainController._getAllCompletedJsonSuperS3__BETTER()

@everything_bp.route('/s3/getAllFilesS3')
def getAllFilesS3_Route():
    return mainController.getAllFilesS3(True)

@everything_bp.route('/s3/getUploadedAudioS3')
def getUploadedAudioS3_Route():
    return mainController.getUploadedAudioS3()

@everything_bp.route('/s3/createCaptionTodoList4Whispher')
def createCaptionTodoList4Whispher_Route():
    return mainController.createCaptionTodoList4Whispher(True)

