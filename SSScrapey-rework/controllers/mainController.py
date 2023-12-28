import urllib

import controllers.MicroPreper.seleniumPreper as seleniumPreper
import controllers.MicroPreper.TodoPreper as todoPreper
import controllers.MicroPreper.databasePreper as databasePreper
import controllers.MicroDownloader.downloader as downloader
import controllers.MicroTranscriber.transcriber as transcriber
import mocks.initScrapData
import mocks.initHrefsData
import mocks.ytdlObjMetaDataList
import datetime
import os
import json
import boto3
from models.AudioResponse import AudioResponse
from models.VodS3Response import VodS3Response
from models.Metadata_Ytdl import Metadata_Ytdl
from models.ScrappedChannel import ScrappedChannel
from controllers.MicroDownloader.Vod import Vod
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
    # Setup. Get Vod
    vods: List[Vod] = transcriber.getTodoFromDb()
    vod = vods[0] if len(vods) > 0 else None
    print('IN THEORY, AUDIO TO TEXT THIS:')
    if not vod and not isDebug:
        print("jk, vod is null, nothing to do")
        return "NOTHING TO DO NO VODS READY"
    if (isDebug):
        vod.print() if vod else print("Null nod")
        # tuple =  ('40792901', 'nmplol', 'And you will know my name is the LORD', '78', '1:18', 39744, 'https://www.twitch.tv/videos/40792901', datetime.datetime(2013, 8, 2, 18, 26, 30), 'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/511e8d0d2a/nmplol_6356312704_6356312704/thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/nmplol/40792901/And_you_will_know_my_name_is_the_LORD-v40792901.opus', '-1', 'English')
        tuple =  ('1964894986', 'jd_onlymusic', '夜市特攻隊「永和樂華夜市」ft. 陳老師', '732', '12:12', 1205, 'https://www.twitch.tv/videos/1964894986', datetime.datetime(2023, 10, 2, 18, 26, 30), 'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d3vd9lfkzbru3h/e8c73b0847f78c0231fc_jd_onlymusic_40759279447_1698755215//thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/jd_onlymusic/1964894986/ft.-v1964894986.opus', '-3', 'Chinese')
        Id, ChannelNameId, Title, Duration, DurationString, ViewCount, WebpageUrl, UploadDate, TranscriptStatus, Priority, Thumbnail, TodoDate, S3Audio, ChanCurrentRank, Language  = tuple
        vod = Vod(id=Id, title=Title, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, todo_date=TodoDate, upload_date=UploadDate, s3_audio=S3Audio, language=Language)
    vod.print()

    # Set TranscrptStatus = "processing"
    transcriber.setSemaphoreDb(vod)

    # All of Transcribing
    try:
        relative_path = transcriber.downloadAudio(vod)
        saved_caption_files = transcriber.doWhisperStuff(vod, relative_path)
        
        for filename in saved_caption_files: # [climb_to_chall.json, climb_to_chall.vtt]
            transcriber.uploadCaptionsToS3(filename, vod)
            transcriber.setCompletedStatusDb(vod)
    except Exception as e:
        print(f"ERROR Transcribing vod: {e}")
        vod.print()
        transcriber.unsetProcessingDb(vod)

    transcriber.cleanUpFiles(relative_path)
    print("Finished step 3 Transcriber-Service")
    return "Finished step 3 Transcriber-Service"










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




