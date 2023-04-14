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

@download_bp.route('/saveTopChannels')
def saveTopChannels_Route():
    return saveTopChannels(None)

@download_bp.route('/getTopChannels')
def getTopChannels_Route():
    return getTopChannels()

@download_bp.route('/getTopChannelsAndSave')
def getTopChannelsAndSave_Route():
    return getTopChannelsAndSave()


@download_bp.route('/initScrape')
def initScrape_Route():
    return initScrape()
