######################################
# 
# 
# THIS IS JUST A TEST HELPER. LIKE A UI
# 
# 
#####################################

import urllib

import controllers.MicroPreper.seleniumPreper as seleniumPreper
import controllers.MicroPreper.TodoPreper as todoPreper
import controllers.MicroPreper.databasePreper as databasePreper
import controllers.MicroDownloader.downloader as downloader
import controllers.MicroTranscriber.audio2text_app as audio2text
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
    
    # Make http request to sullygnome. 3rd party website
    topChannels = todoPreper.getTopChannels() 

    # Convert json respone to objects
    scrapped_channels: List[ScrappedChannel] = todoPreper.instantiateJsonToClassObj(topChannels) # relevant_data = /mocks/initScrapData.py
    scrapped_channels: List[ScrappedChannel]  = todoPreper.addVipList(scrapped_channels) # same ^ but with gera

    # Via selenium & browser. Find videos's url, get anchor tags href
    if isDebug:
        scrapped_channels: List[ScrappedChannel] = mocks.initHrefsData.getHrefsData()
        # print(json.dumps(scrapped_channels, default=lambda o: o.__dict__, indent=4))
    else:
        scrapped_channels: List[ScrappedChannel] = seleniumPreper.scrape4VidHref(scrapped_channels, isDebug) # returns -> /mocks/initHrefsData.py

    # Done
    databasePreper.updateDb1(scrapped_channels)
    print("Finished step 1 Preper-Service")
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








# ####################################################
# ####################################################
# ####################################################
# ####################################################
# ####################################################
# ####################################################
# ####################################################
# ####################################################
# ####################################################
# ####################################################
# ####################################################
# ####################################################
# ####################################################

# # Expected S3 query:
# # Key= channels/vod-audio/lck/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.json
# # Key= channels/vod-audio/lck/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.mp3
# # Key= channels/vod-audio/lck/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.vtt
# # Key= channels/vod-audio/lck/576354726/metadata.json
# # Key= channels/vod-audio/lolgeranimo/28138895/The Geraniproject! I Love You Guys!!!-v28138895.json
# # Key= channels/vod-audio/lolgeranimo/28138895/The Geraniproject! I Love You Guys!!!-v28138895.mp3
# # Key= channels/vod-audio/lolgeranimo/28138895/The Geraniproject! I Love You Guys!!!-v28138895.vtt
# # Key= channels/vod-audio/lolgeranimo/28138895/metadata.json
# # Key= channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.json
# # Key= channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3
# # Key= channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.vtt
# # Key= channels/vod-audio/lolgeranimo/5057810/metadata.json
# # return = 
# # {
# #   "lck": {
# #              "28138895": ["Geraniproject.json", "Geraniproject.mp3", "Geraniproject.vtt"],
# #              "5057810": ["Calculated.json", "Calculated.mp3", "Calculated.vtt"],
# #          }
# #   "lolgeranimo" ... 
# # }
# def _getAllCompletedJsonSuperS3__BETTER(): # -> mocks/getAllCompletedJsonSuperS3__BETTER.py
#     s3 = boto3.client('s3')
#     objects = s3.list_objects_v2(Bucket=env_varz.BUCKET_NAME, Prefix=env_varz.S3_CAPTIONS_KEYBASE)['Contents']
#     sorted_objects = sorted(objects, key=lambda obj: obj['Key'])
#     print("----- _getCompletedAudioJsonSuperS3 ---- ")
    
#     allOfIt = {}
#     for obj in sorted_objects:
#         filename = obj['Key'].split("/")[4:][0]
#         vod_id = obj['Key'].split("/")[3:4][0]
#         channel = obj['Key'].split("/")[2:3][0]
#         # print("@@@@@@@@@@@@@@@@@@@@@")
#         # print("Key= " + f"{obj['Key']}")
#         # print("channel: " +  (channel))     
#         # print("vod_id: " +  (vod_id))
#         # print("filename: " + (filename))
#         # 1. obj[key] = channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3
#         # 2. temp = lolgeranimo/5057810/Calculated-v5057810.mp3
#         # 3. channel, vod_i, vod_title = [ lolgeranimo, 5057810, "Calculated-v5057810.mp3" ] 
#         temp = str(obj['Key']).split(env_varz.S3_CAPTIONS_KEYBASE, 1)[1]   # 2
#         # channel, vod_id, vod_title = temp.split("/", 2)[:3] # 3 
#         if allOfIt.get(channel):
#             if allOfIt.get(channel).get(vod_id): # if vod_id for channel exists
#                 allOfIt.get(channel).get(vod_id).append(filename)
#             else: # else create a list that has all filenames
#                 allOfIt.get(channel)[vod_id] = [filename]
#         else:
#             vod_dict = { vod_id: [filename] }
#             allOfIt[channel] = vod_dict
#     print ()
#     print ("(_getAllCompletedJsonSuperS3__BETTER) allOfIt=")
#     print (json.dumps(allOfIt, default=lambda o: o.__dict__, indent=4))
#     print ()
#     # for key, value in allOfIt.items():
#     #     print(key + ": " + str(value))
#     return allOfIt




