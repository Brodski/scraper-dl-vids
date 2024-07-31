#####################################
#                                   #
#                                   #
#                                   #
#            TEST FILE              #
#      (used to help me test)       #
#                                   #
#                                   #
#                                   #
#####################################

import urllib

import controllers.MicroDownloader.downloader as downloader
import controllers.MicroTranscriber.transcriberGo as audio2text
import controllers.MicroPreper.preperGo as preperGo
import controllers.MicroDownloader.downloaderGo as downloadGo
import mocks.initHrefsData
import datetime
import os
import json
from models.ScrappedChannel import ScrappedChannel
from models.Vod import Vod
from typing import List

import env_file as env_varz

####################################################
# Kickit()
#
# Does everything.
# API sully gnome - Gets top channels 
# Selenium  - gets vods
# ytdl      - downloads new vods
# ffmpeg    - compresses audio
# S3        - uploads audio
# S3        - updates completed json
#####################################################
#
#       Microservice 1
#
#####################################################
def kickit(isDebug=False):
    preperGo.prepare(isDebug)
    return "Finished step 1 Preper-Service"

#####################################################
#
#       Microservice 2
#
#####################################################

def kickDownloader(isDebug=False):
    x = downloadGo.goDownloadBatch(isDebug)
    print('Finished kickDownloader')
    return x

#####################################################
#
#       Microservice 3 VAST AI
#
#####################################################

def kickWhisperer(isDebug=False):
    audio2text.goTranscribeBatch(isDebug)
    return "Woooo! done!"

