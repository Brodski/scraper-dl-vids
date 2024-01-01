######################################
# 
# 
# THIS IS JUST A TEST HELPER. LIKE A UI
# 
# 
#####################################

import urllib

import controllers.MicroDownloader.downloader as downloader
import controllers.MicroTranscriber.audio2text_app as audio2text
import controllers.MicroPreper.preperGo as preperGo
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
    preperGo.gogo(isDebug)
    return "Finished step 1 Preper-Service"

#####################################################
#
#       Microservice 2
#
#####################################################

def kickDownloader(isDebug=False):
    # Setup. Get vod
    vods_list: List[Vod] = downloader.getTodoFromDatabase(isDebug=isDebug) # limit = 5
    vod: Vod = downloader.getNeededVod(vods_list)
    if isDebug:
        # vod = Vod(id="40792901", channels_name_id="nmplol", transcript="todo", priority=-1, channel_current_rank="-1") # (Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
        vod = Vod(id="1964894986", channels_name_id="jd_onlymusic", transcript="todo", priority=0, channel_current_rank="-1") # (Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
        print("doing this vod:")
        print(vod.print())

    # Download vod from twitch
    downloaded_metadata = downloader.downloadTwtvVid2(vod, True)
    if downloaded_metadata == "403":
        downloader.updateUnauthorizedVod(vod)
        return "nope gg sub only"
    
    # Post process vod
    downloaded_metadata = downloader.removeNonSerializable(downloaded_metadata)
    downloaded_metadata, outfile = downloader.convertVideoToSmallAudio(downloaded_metadata)

    # Upload
    s3fileKey = downloader.uploadAudioToS3_v2(downloaded_metadata, outfile, vod)
    if (s3fileKey):
        downloader.updateVods_Round2Db(downloaded_metadata, vod.id, s3fileKey)
    downloader.cleanUpDownloads(downloaded_metadata)

    print("Finished step 2 Downloader-Service")
    return downloaded_metadata


#####################################################
#
#       Microservice 3
#
#####################################################

def kickWhisperer(isDebug=False):
    audio2text.gogo(isDebug)
    return "Woooo! done!"

