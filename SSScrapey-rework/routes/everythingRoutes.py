import json
from typing import List
from flask import Blueprint
from flask import jsonify
import controllers.MicroPreper.seleniumPreper as seleniumPreper
import controllers.mainController as mainController
import controllers.MicroPreper.TodoPreper as TodoPreper
import controllers.MicroTranscriber.transcriber as transcriber

#variable is used in app.py
everything_bp = Blueprint('download', __name__)
ranking_bp = Blueprint('ranking', __name__)


####################################################
@everything_bp.route('/main/ranking/kickit')
def kickit_Route():
    return mainController.kickit(True)

@everything_bp.route('/main/ranking/kickit_real')
def kickit_real_Route():
    return mainController.kickit(False)

@ranking_bp.route('/getTopChannelsSully')
def getTopChannelsSully_Route():
    return TodoPreper.getTopChannelsSully(isDebug=True)
#################################################
# 1 Preper
#################################################
@everything_bp.route('/hrefGet/scrape4VidHref/mock')
def scrape4VidHref_Route():
    return seleniumPreper.scrape4VidHref({}, True)



#################################################
# 2 Downloader
#################################################
@everything_bp.route('/main/kickDownloader')
def kickDownloader_Route():
    return mainController.kickDownloader(True)

@everything_bp.route('/main/kickDownloader_real')
def kickDownloader_real_Route():
    return mainController.kickDownloader(False)

#################################################
# 3 Transcriber
#################################################
@everything_bp.route('/main/kickTranscriber/kickIt')
def kickTranscriber_Route():
    return mainController.kickWhisperer(True)

@everything_bp.route('/main/kickTranscriber/kickIt_real')
def kickTranscriber_real_Route():
    return mainController.kickWhisperer(False)


@everything_bp.route('/main/kickTranscriber/getTodoFromDb')
def kickTranscriber_getTodoFromDb_Route():
    return transcriber.getTodoFromDb()
