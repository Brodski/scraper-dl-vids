import urllib
# from controllers.yt_download import uploadAudioToS3
import controllers.seleniumController as seleniumController
import controllers.rankingController as rankingController
import mocks.initScrapData
import mocks.initHrefsData
import mocks.ytdlObjMetaDataList
import controllers.yt_download as yt
import datetime
import json
import boto3
from models.AudioResponse import AudioResponse
from models.VodS3Response import VodS3Response
from models.Vod import Vod
from typing import List

import env_app as env_varz

import ast

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
def kickit(isDebug=False):
    
    # Make http request to sullygnome. 3rd party website
    topChannels = rankingController.getTopChannels() 
    relavent_data = rankingController.tidyData(topChannels) # relavent_data = /mocks/initScrapData.py
    relavent_data = rankingController.addVipList(relavent_data) # same ^ but with gera

    if isDebug:
        print ("ENDING PREMPTIVELY B/C is DEBUG")
        return relavent_data
    initYtdlAudio(relavent_data, isDebug=isDebug)
    return "Finished kickit()"
####################################################

def kickit_just_gera(isDebug=False):
    relavent_data = rankingController.addVipList([]) # same ^ but with gera
    initYtdlAudio(relavent_data, isDebug=isDebug)
    return "JUST GERA DONE!"



#####################################################
# Comes after 3                                     #
# TODO                                              #
# calls yt.addTodoDownlaods(channels)
# calls yt.scrape4VidHref(^)
# calls yt.addTodoListS3(^)
def initYtdlAudio(channels, *, isDebug=False):
    print ("00000000000000                 00000000000000000")
    print ("00000000000000  initYtdlAudio  00000000000000000")
    print ("00000000000000                 00000000000000000")
    # TODO probably need some interface & models for the scrapped-data vs ytdl-data
    if isDebug:
        scrapped_channels = mocks.initHrefsData.getHrefsData()
    else:
        scrapped_channels = seleniumController.scrape4VidHref(channels, isDebug) # returns -> /mocks/initHrefsData.py
        
    print("     (initYtdlAudio) scrapped_channels")
    print("     (initYtdlAudio) " + str(scrapped_channels))
    scrapped_channels_with_todos = yt.addTodoListS3(scrapped_channels)  # returns -> /mocks/scrapped_channels_with_todos.py
    print ("     (initYtdlAudio) scrapped_channels_with_todos=")
    print (str(scrapped_channels_with_todos))

    # Download X vids from Y channels
    metadata_Ytdl_list = yt.bigBoyChannelDownloader(scrapped_channels_with_todos, isDebug=isDebug)
    print("     (initYtdlAudio) ++++++++++++++++++++++++++")
    print("     (initYtdlAudio) ++++++++++++++++++++++++++")
    print("     (initYtdlAudio) ++++++++++++++++++++++++++")
    print("     (initYtdlAudio) DOWNLOADED THESE:")
    print (metadata_Ytdl_list)
    for yt_meta in metadata_Ytdl_list:       
        print (   "(initYtdlAudio) - " + yt_meta.channel + " @ " + yt_meta.metadata.get("title"))
    for yt_meta in metadata_Ytdl_list:        
        # SEND mp3 & metadata TO S3 --> channels/vod-audio/<CHN>/<DATE>/<ID>.mp3 .. yt_meta has mp3 file location
        yt.uploadAudioToS3(yt_meta, isDebug) 

    createTodoList4Whispher()
    print("COMPLEEEEEEEEEEEEEEEEEETE")
    return "Compelte init"



def createTodoList4Whispher(isDebug=False):
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    print('zzzzzz           createTodoList4Whispher            zzzzzzz')
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    allOfIt = _getAllCompletedJsonSuperS3__BETTER() # lotsOfData = mocks/completedJsonSuperS3.py
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')

    if allOfIt is None or len(allOfIt)==0:
        raise Exception("Something is wrong with '_getCompletedAudioJsonSuperS3' audio json file")
    # print ("allOfIt")
    # print (allOfIt)
    # print (json.dumps(allOfIt, default=lambda o: o.__dict__, indent=4))
    captions_ext = ['.json', '.vtt']
    missing_captions_list = []

    for k_chn, v_id_files in allOfIt.items():
        print(k_chn)
        for id, files in v_id_files.items():
            # print ()
            # print ("    " + str(id))
            # print ("    " + str(files))
            # hasAudio = False
            hasCaptions = False
            for file in files:
                if file == "metadata.json":
                    continue
                if file[-5:] not in captions_ext and file[-4:] not in captions_ext:
                    hasAudio = True
                    vod_title = file
                    continue
                if file[-5:] in captions_ext or file[-4:] in captions_ext:
                    hasCaptions = True
            if hasAudio and not hasCaptions:
                print("MISSING CAPTIONS for: " + k_chn + " " + id)
                print()
                vod = Vod(channel=k_chn, id=id, title=urllib.parse.unquote(vod_title))
                vod_encode = urllib.parse.quote(vod.title)
                vod_path = env_varz.S3_CAPTIONS_KEYBASE + vod.channel + "/" + vod.id + "/" + vod_encode
                vod.link_s3 =  env_varz.BUCKET_DOMAIN + "/" + vod_path

                missing_captions_list.append(vod)
    s3 = boto3.client('s3')
    s3.put_object(Body=json.dumps(missing_captions_list, default=lambda o: o.__dict__), Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_TODO_AUDIO)
    print ("MISSSING!")
    print ("MISSSING!")
    print ("MISSSING!")
    print ("MISSSING!")
    print (missing_captions_list)
    print (json.dumps(missing_captions_list, default=lambda o: o.__dict__, indent=4))
    if isDebug:
        return json.loads(json.dumps(missing_captions_list, default=lambda o: o.__dict__)) 
    return missing_captions_list




# Expected S3 query:
# Key= channels/vod-audio/lck/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.json
# Key= channels/vod-audio/lck/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.mp3
# Key= channels/vod-audio/lck/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.vtt
# Key= channels/vod-audio/lck/576354726/metadata.json
# Key= channels/vod-audio/lolgeranimo/28138895/The Geraniproject! I Love You Guys!!!-v28138895.json
# Key= channels/vod-audio/lolgeranimo/28138895/The Geraniproject! I Love You Guys!!!-v28138895.mp3
# Key= channels/vod-audio/lolgeranimo/28138895/The Geraniproject! I Love You Guys!!!-v28138895.vtt
# Key= channels/vod-audio/lolgeranimo/28138895/metadata.json
# Key= channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.json
# Key= channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3
# Key= channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.vtt
# Key= channels/vod-audio/lolgeranimo/5057810/metadata.json
# return = 
# {
#   "lck": {
#              "28138895": ["Geraniproject.json", "Geraniproject.mp3", "Geraniproject.vtt"],
#              "5057810": ["Calculated.json", "Calculated.mp3", "Calculated.vtt"],
#          }
#   "lolgeranimo" ... 
# }
def _getAllCompletedJsonSuperS3__BETTER(): # -> mocks/completedJsonSuperS3.py
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket=env_varz.BUCKET_NAME, Prefix=env_varz.S3_CAPTIONS_KEYBASE)['Contents']
    sorted_objects = sorted(objects, key=lambda obj: obj['Key'])
    print("----- _getCompletedAudioJsonSuperS3 ---- ")
    
    allOfIt = {}
    for obj in sorted_objects:
        filename = obj['Key'].split("/")[4:][0]
        vod_id = obj['Key'].split("/")[3:4][0]
        channel = obj['Key'].split("/")[2:3][0]
        print("@@@@@@@@@@@@@@@@@@@@@")
        print("Key= " + f"{obj['Key']}")
        print("channel: " +  (channel))     
        print("vod_id: " +  (vod_id))
        print("filename: " + (filename))
        # 1. obj[key] = channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3
        # 2. temp = lolgeranimo/5057810/Calculated-v5057810.mp3
        # 3. channel, vod_i, vod_title = [ lolgeranimo, 5057810, "Calculated-v5057810.mp3" ] 
        temp = str(obj['Key']).split(env_varz.S3_CAPTIONS_KEYBASE, 1)[1]   # 2
        # channel, vod_id, vod_title = temp.split("/", 2)[:3] # 3 
        if allOfIt.get(channel):
            if allOfIt.get(channel).get(vod_id): # if vod_id for channel exists
                allOfIt.get(channel).get(vod_id).append(filename)
            else: # else create a list that has all filenames
                allOfIt.get(channel)[vod_id] = [filename]
        else:
            vod_dict = { vod_id: [filename] }
            allOfIt[channel] = vod_dict
    print ()
    print ("(_getAllCompletedJsonSuperS3__BETTER) allOfIt=")
    print (json.dumps(allOfIt, default=lambda o: o.__dict__, indent=4))
    print ()
    # for key, value in allOfIt.items():
    #     print(key + ": " + str(value))
    return allOfIt








###########################################################################################################################################################
###########################################################################################################################################################
###########################################################################################################################################################
###########################################################################################################################################################
###########################################################################################################################################################
###########################################################################################################################################################
###########################################################################################################################################################
###########################################################################################################################################################
###########################################################################################################################################################
###########################################################################################################################################################
###########################################################################################################################################################

####################################################
# 2                                                #
# IntializeScrape                                  #
# WE CAN PROB IGNORE THIS                          
# THIS IS JUST FOR THST CHECKY "GET FEW BEFORE"
# def getChannelFromS3(): # -> return data = kickit() = json_data
#     return "COMMENTED OUT CODE!!! junk"
    # # We first get the key/paths from the s3
    # # sorted_s3_paths = rankingController.preGetChannelInS3AndTidy() # returns a List[str] of S3 Keys/Paths that point to the save s3 channels:
    # # combined_channels_list = rankingController.getChannelInS3AndTidy(sorted_s3_paths) # returns a List[{dict}] of channels and culled date
    # combined_channels_list = rankingController.getChannelInS3AndTidy() # returns a List[{dict}] of channels and culled date
    # combined_channels_list = rankingController.addVipList(combined_channels_list) # ^ but with gera
    # # Returns: 
    #     #     {
    #     #     "displayname": "LoLGeranimo",
    #     #     "language": "English",
    #     #     "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
    #     #     "twitchurl": "https://www.twitch.tv/lolgeranimo",
    #     #     "url": "lolgeranimo"
    #     #   },...,
    # return combined_channels_list
#                                                   #
#####################################################

# Query the s3 with the formated json of top channels
# def preGetChannelInS3AndTidy() -> List[str]:  
#     return "commented out code"
    # # - Note boto3 returns last modified as: datetime.datetime(2023,4,10,7,44,12,"tzinfo=tzutc()
    # # Thus
    # #     obj['Key']          = channels/ranking/raw/2023-15/100.json = location of metadata
    # #     obj['LastModified'] = Last modified: 2023-04-11 06:54:39+00:00

    
    # # REACH_BACK_DAYS = Content / UX thing
    # # Recall, our S3 saves top X channels every day, REACH will allow us to grab a couple more channels incase 
    # # a channel begins to slip in ranking not b/c of popularity but b/c IRL stuff or w/e
    # #
    # REACH_BACK_DAYS = 5
    # s3 = boto3.client('s3')
    # # TODO env var this Prefix
    # objects = s3.list_objects_v2(Bucket=env_varz.BUCKET_NAME, Prefix="channels/ranking/")['Contents']
    # sorted_objects = sorted(objects, key=lambda obj: obj['LastModified'])
    # print("-----SORTED (OFFICIAL)---- " + str(REACH_BACK_DAYS) + " days ago")
    # keyPathList = []
    # sorted_objects = sorted_objects[-REACH_BACK_DAYS:]
    # for obj in sorted_objects:
    #     print("Key= " + f"{obj['Key']} ----- Last modified= {obj['LastModified']}")
    #     keyPathList.append(obj['Key'])
    # return keyPathList

# def getChannelInS3AndTidy(sorted_s3_paths):
#     s3 = boto3.client('s3')
#     objects = s3.list_objects_v2(Bucket=env_varz.BUCKET_NAME, Prefix="channels/ranking/")['Contents']
#     sorted_objects = sorted(objects, key=lambda obj: obj['LastModified'])
#     keyPathList = []
#     for obj in sorted_objects:
#         print("Key= " + f"{obj['Key']} ----- Last modified= {obj['LastModified']}")
#         keyPathList.append(obj['Key'])
#     # return keyPathList

#     print("GETTING ALL CONTENT")
#     relevant_list = []
#     already_added_list = []
#     for key in sorted_s3_paths:
#         print(key)
#         responseGetObj = s3.get_object(
#             Bucket = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket',
#             Key = key # ex) 'channels/ranking/2023-04-14.json'
#         )
#         binary_data = responseGetObj['Body'].read()
#         json_string = binary_data.decode('utf-8')
#         json_object = json.loads(json_string) # { "data":[ { "viewminutes":932768925, "streamedminutes":16245, ... } ] }

#         llist = tidyData(json_object)
#         for channel in llist:
#             if channel.get('displayname') in already_added_list:
#                 continue
#             already_added_list.append(channel.get('displayname'))
#             relevant_list.append(channel)
#     print ("WE DONE")
#     for r in relevant_list:
#         print (r['displayname'])
#     return relevant_list