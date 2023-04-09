from flask import Blueprint
from flask import jsonify
import asyncio
# const express = require("express");
# const router = express.Router();
from controllers.downloadController import scrapePage, aggregateChannels
# const { getUsers, makeUser, getUser, somethingTime } = require("../controllers/users");
# router.get('/', getUsers);

download_bp = Blueprint('download', __name__)

@download_bp.route('/channel/<name>')
async def getVidPaths(name=""):
    if name == "":
        return   
    return await scrapePage(name)

    

@download_bp.route('/channel/getAll')
def download_editor():
    #                                                                 type3=most watched
    #                                                   /30days/0?/#clicks?/type/desc/start/get100streams
    #  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/1/3/desc/0/100
    #  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/2/3/desc/100/100
    #  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/3/3/desc/200/100
    #  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/4/3/desc/300/100
    #  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/1/5/desc/0/100

                                                # type6=avg-viewers
    # https://sullygnome.com/api/tables/channeltables/getchannels/30/0/11/6/desc/0/100

    loopMax = 15
    pageSize = 100
    type = 3 # 3 = Most watched = net society time watching .... 3 = average viewers
    for i in range(loopMax):
        print (f'https://sullygnome.com/api/tables/channeltables/getchannels/30/0/{str(i)}/{type}/desc/{str(i * pageSize)}/{str(pageSize)}')

    url = 'https://sullygnome.com/api/tables/channeltables/getchannels/30/0/0/3/desc/0/100'
    return aggregateChannels(url)

@download_bp.route('/date')
def download_date():
    return 'Blog Date'