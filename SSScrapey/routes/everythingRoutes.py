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
import mocks.completed_captions_list
import mocks.big_key_val_list
import mocks.relevant_data

#variable is used in app.py
everything_bp = Blueprint('download', __name__)
ranking_bp = Blueprint('ranking', __name__)


####################################################
# 1
# Make http request to sullygnome. 3rd party website
# Decide who we want to look at
# Saves to S3
@everything_bp.route('/main/ranking/kickit')
def kickit_Route():
    return mainController.kickit(True)

@ranking_bp.route('/getTopChannels')
def getTopChannels_Route():
    return rankingController.getTopChannels(isDebug=True)

####################################################



####################################################

@everything_bp.route('/main/ytdl/initYtdlAudio')
def initYtdlAudio_Route():
    return mainController.initYtdlAudio({}, isDebug=True) # isDebuging = True

@everything_bp.route('/main/ytdl/bigBoyChannelDownloader_TEST')
def bigBoyChannelDownloader_TEST_Route():
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
            "todos":["/576354726/", "/1108764940/"]
            }
        ],
    isDebug=True
    )
    return json.loads(json.dumps(metadata_Ytdl_list, default=lambda o: o.__dict__))



@everything_bp.route('/ytdl/test/downloadTwtvVid_FIXED')
def downloadTwtvVid_FIXED_Route():
    # x = ytdl.downloadTwtvVid("/videos/5057810")
    # x = ytdl.downloadTwtvVid("/videos/28138895")
    x = ytdl.downloadTwtvVid("https://www.youtube.com/watch?v=R4g5jUqatFk")
    return str(x)

@everything_bp.route('/ytdl/getAlreadyDownloadedS3_TEST')
def getAlreadyDownloadedS3_Route():
    return ytdl.getAlreadyDownloadedS3_TEST("lolgeranimo", ['/videos/5057810', '/videos/28138895', '/videos/6666666'])




@everything_bp.route('/hrefGet/scrape4VidHref/mock')
def scrape4VidHref_Route():
    return seleniumController.scrape4VidHref({}, True)


@everything_bp.route('/s3/_getAllCompletedJsonSuperS3__BETTER')
def _getAllCompletedJsonSuperS3__BETTER_Route():
    return mainController._getAllCompletedJsonSuperS3__BETTER()


@everything_bp.route('/s3/uploadTodoAndCompletedJsons')
def uploadTodoAndCompletedJsons_Route():
    return mainController.uploadTodoAndCompletedJsons(True)

@everything_bp.route('/s3/uploadLightOverviewS3')
def uploadLightOverviewS3_Route():
    return mainController.uploadLightOverviewS3(mocks.big_key_val_list.get_big_key_val_list(), mocks.relevant_data.get_relevant_data())

@everything_bp.route('/s3/uploadEachChannelsCompletedJson')
def uploadEachChannelsCompletedJson_Route():
    return mainController.uploadEachChannelsCompletedJson(mocks.completed_captions_list.get_completed_captions_list())

@everything_bp.route('/s3/uploadOverviewStateS3')
def uploadOverviewStateS3_Route():
    return mainController.uploadOverviewStateS3()

@everything_bp.route('/main/kickit_just_gera')
def kickit_just_gera_Route():
    return mainController.kickit_just_gera(True)

