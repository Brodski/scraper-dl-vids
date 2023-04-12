from flask import Blueprint
from flask import jsonify
import asyncio
# const express = require("express");
# const router = express.Router();
from controllers.downloadController import *
# or "import controllers.downloadController"
# --> controllers.downloadController.uploadJsonToS3
# const { getUsers, makeUser, getUser, somethingTime } = require("../controllers/users");
# router.get('/', getUsers);

download_bp = Blueprint('download', __name__)

@download_bp.route('/testGetTop500Channels_NameCompleted')
def testGetTop500Channels_NameCompleted_Route():
    return testGetTop500Channels_NameCompleted()

@download_bp.route('/getAllS3Jsons')
def getAllS3Jsons_Route():
    return getAllS3Jsons()

@download_bp.route('/uploadJsonToS3Test')
def uploadJsonToS3_Route():
    return uploadJsonToS3Test()

@download_bp.route('/doS3Stuff')
def doS3Stuff_Route():
    return doS3Stuff()

@download_bp.route('/channel/<name>')
async def getVidPaths(name=""):
    if name == "":
        return   
    return await scrapePage(name)

    

@download_bp.route('/channel/uploadChannelsJsonToS3')
def uploadChannelsJsonToS3_Route():
    #                                                                 type3=most watched
    #                                                   /30days/0?/#clicks?/type/desc/start/get100streams
    #  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/1/3/desc/0/100
    #  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/2/3/desc/100/100
    #  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/3/3/desc/200/100
    #  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/4/3/desc/300/100
    #  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/1/5/desc/0/100

                                                # type6=avg-viewers
    # https://sullygnome.com/api/tables/channeltables/getchannels/30/0/11/6/desc/0/100

    return uploadChannelsJsonToS3()

@download_bp.route('/date')
def download_date():
    return 'Blog Date'