import urllib

import requests
# from controllers.yt_download import uploadAudioToS3
import controllers.seleniumController as seleniumController
import controllers.rankingController as rankingController
import mocks.initScrapData
import mocks.initHrefsData
import mocks.ytdlObjMetaDataList
import controllers.yt_download as yt
import datetime
import os
import json
import boto3
from models.AudioResponse import AudioResponse
from models.VodS3Response import VodS3Response
from models.Metadata_Ytdl import Metadata_Ytdl
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
    relevant_data = rankingController.tidyData(topChannels) # relevant_data = /mocks/initScrapData.py
    relevant_data = rankingController.addVipList(relevant_data) # same ^ but with gera

    if isDebug and os.getenv("ENV") == "local":
        print ("ENDING PREMPTIVELY B/C is DEBUG")
        return relevant_data
    metadata_Ytdl_list = initYtdlAudio(relevant_data, isDebug=isDebug)
    
    doUploadStuff(relevant_data, metadata_Ytdl_list)


    return "Finished kickit()"
####################################################

def kickit_just_gera(isDebug=False):
    relevant_data = rankingController.addVipList([]) # same ^ but with gera
    metadata_Ytdl_list = initYtdlAudio(relevant_data, isDebug=isDebug) # relevant_data = data from gnome api

    if not isDebug:
        doUploadStuff(relevant_data, metadata_Ytdl_list)

    return "JUST GERA DONE!"

def doUploadStuff(relevant_data, metadata_Ytdl_list):
    
    for yt_meta in metadata_Ytdl_list:
        yt.uploadAudioToS3(yt_meta) 
        
        data_custom = createCustomMetadata(yt_meta)
        manage_data(data_custom)

    [missing_captions_list, completed_captions_list] = uploadTodoAndCompletedJsons()
    uploadOverviewStateS3()
    big_key_val_list = uploadEachChannelsCompletedJson(completed_captions_list)
    uploadLightOverviewS3(big_key_val_list, relevant_data)

#####################################################
#                                                   #
#                                                   #
# calls yt.addTodoDownlaods(channels)
# calls yt.scrape4VidHref(^)
# calls yt.addTodoListS3(^)
def initYtdlAudio(channels, *, isDebug=False):
    print ("00000000000000                 00000000000000000")
    print ("00000000000000  initYtdlAudio  00000000000000000")
    print ("00000000000000                 00000000000000000")

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
    if isDebug:
        return json.dumps(metadata_Ytdl_list, default=lambda o: o.__dict__)
    return metadata_Ytdl_list

def manage_data(data_custom):
    # S3_CUSTOM_METADATA_BASE = 'channels/completed-jsons/custom-metadata/'
    
    s3 = boto3.client('s3')
    
    vod_id = data_custom.get('id')
    channel = data_custom.get('channel')
    
    key = env_varz.S3_CUSTOM_METADATA_KEYBASE + channel + "/custom-metadata.json"

    print(json.dumps(data_custom, indent=4))
    print("key=" + key)

    try:
        resS3 = s3.get_object(Bucket=env_varz.BUCKET_NAME, Key=key)
        custom_metadata_json_file = json.loads(resS3["Body"].read().decode("utf-8"))
    except:
        print("Does not exist")
        custom_metadata_json_file = {}

    print("custom_metadata_s3")
    print(custom_metadata_json_file)

    vod_metadata = custom_metadata_json_file.get(vod_id)

    if not vod_metadata:
        print("NOT!!!!!!!!!")
        vod_metadata = {}
    for k, value in data_custom.items():
        print(f'{k}: {value}')
        vod_metadata[k] = value
        # if k == "channel":
        #     continue

    custom_metadata_json_file[vod_id] = vod_metadata
    
    print("custom_metadata")
    print("custom_metadata")
    print("custom_metadata")
    print("custom_metadata")
    print(json.dumps(custom_metadata_json_file , indent=4))
    # s3.put_object(Body=json.dumps(custom_metadata_json_file, default=lambda o: o.__dict__), Bucket=BUCKET_NAME, Key=key)

    return 'done X'



# See "manage_dataz()" in custom-metadata-appy.py
def createCustomMetadata(yt_meta: Metadata_Ytdl): # 
    print("yt_meta")
    print("yt_meta")
    print(yt_meta.__dict__)
    data = {
        'id': yt_meta.metadata["id"][1:],
        'channel': yt_meta.channel,
        "display_title": yt_meta.metadata["title"],
        "duration": yt_meta.metadata["duration"],
        "thumbnail": yt_meta.metadata["thumbnail"],
        "display_title": yt_meta.metadata["title"],
        "timestamp": yt_meta.metadata["timestamp"],
        "view_count": yt_meta.metadata["view_count"],
        "upload_date": yt_meta.metadata["upload_date"],
        "duration_string": yt_meta.metadata["duration_string"],
        "epoch": yt_meta.metadata["requested_downloads"][0]["epoch"],
        "fulltitle": yt_meta.metadata["fulltitle"]
    }

    print("data")
    print("data")
    print("data")
    print("data")
    print("data")
    print(data)
    return data



# could be better
def uploadTodoAndCompletedJsons(isDebug=False):
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    print('zzzzzz           uploadTodoAndCompletedJsons            zzzzzzz')
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    allOfIt = _getAllCompletedJsonSuperS3__BETTER() # lotsOfData = mocks/get_all_superS3__BETTER.py.py
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')

    if allOfIt is None or len(allOfIt)==0:
        raise Exception("Something is wrong with '_getCompletedAudioJsonSuperS3' audio json file")

    captions_ext = ['.json', '.vtt']
    missing_captions_list = []
    completed_captions_list = []

    for k_chn, v_id_files in allOfIt.items():
        print()
        print(k_chn)
        for id, files in v_id_files.items():
            print()
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
                vod = Vod(channel=k_chn, id=id, title=urllib.parse.unquote(vod_title))
                missing_captions_list.append(vod)
            if hasAudio and hasCaptions:
                print("COMPLETED AUDIO and CAPTIONS for: " + k_chn + " " + id)
                vod = Vod(channel=k_chn, id=id, title=urllib.parse.unquote(vod_title))
                completed_captions_list.append(vod)

    s3 = boto3.client('s3')
    # s3.put_object(Body=json.dumps(missing_captions_list, default=lambda o: o.__dict__), Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_TODO_AUDIO)
    s3.put_object(Body=json.dumps(completed_captions_list, default=lambda o: o.__dict__), Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_CAPTIONS_JSON)
    print ("MISSSING below!")
    print ("MISSSING below!")
    print ("MISSSING below!")
    print ("MISSSING below!")
    print (missing_captions_list)
    print ("COMPLETED below!")
    print ("COMPLETED below!")
    print ("COMPLETED below!")
    print ("COMPLETED below!")
    print (completed_captions_list)
    if isDebug and os.getenv("ENV") == "local":
        return json.loads(json.dumps({"completed_captions_list": completed_captions_list, "missing_captions_list": missing_captions_list}, default=lambda o: o.__dict__))
    return [missing_captions_list, completed_captions_list]

def getIndivChannelKey(chan):
    return env_varz.S3_COMPLETED_INDIV_CHAN_ROOT + chan + ".json"

# returns -> /mocks/light_overview_s3.py
def uploadLightOverviewS3(big_key_val_list, relevant_data): # /mocks/big_key_val_list.py
    # print(str(s3_state_json))
    # print(json.dumps(big_key_val_list, default=lambda o: o.__dict__, indent=4))
    
    # prepped_rel_data = {'lolgeranimo': '-1', 'ibai': 1, 'kaicenat': 2, 'fextralife': 3, 'kingsleague': 4, 'loud_coringa': 5, 'cellbit': 6, 'k3soju': 7, 'handongsuk': 8, 'eliasn97': 9, 'tarik': 10, 'xqc': 11, 'gaules': 12, 'hasanabi': 13, 'paulinholokobr': 14, 'ironmouse': 15, 'nix': 16, 'otplol_': 17, 'esl_dota2': 18, 'fps_shaka': 19, 'paragon_dota': 20}
    prepped_rel_data = {} 
    for chan in relevant_data:
        print("chan")
        print(chan.get("url"))
        # print(chan)
        # print("relevant_data")
        # print(relevant_data)
        prepped_rel_data[chan.get("url")] = {}
        prepped_rel_data[chan.get("url")] = {
            "rownum": chan.get("rownum"),
            "logo": chan.get("logo"),
            "twitchurl": chan.get("twitchurl"),
            "displayname": chan.get("displayname")
        }

    light_overview_list = []
    for chan in big_key_val_list:
        print()
        print()
        print()
        print(chan)        
        rnum = None
        twitchurl = None
        displayname = None
        logo = None
        chanx = prepped_rel_data.get(chan)
        
        print(chanx)
        print(chanx)
        if chanx:
            rnum = chanx.get("rownum")
            twitchurl = chanx.get("twitchurl")
            displayname = chanx.get("displayname")
            logo = chanx.get("logo")
        light_overview_list.append({
            "channel": chan,
            "size": len(big_key_val_list[chan]),
            "path": getIndivChannelKey(chan),
            "rownum": rnum if rnum else "9999",
            "twitchurl": twitchurl,
            "displayname": displayname,
            "logo": logo
        })
    s3 = boto3.client('s3')
    key = env_varz.S3_OVERVIEW_STATE_LIGHT_JSON
    print("UPLOADING LIGHTWEIGHT S3 OVERVIEW:")
    print("upload to: " + key)
    print(json.dumps(light_overview_list, default=lambda o: o.__dict__, indent=4))
    s3.put_object(Body=json.dumps(light_overview_list, default=lambda o: o.__dict__), Bucket=env_varz.BUCKET_NAME, Key=key)
    return json.loads(json.dumps(light_overview_list, default=lambda o: o.__dict__))



def uploadOverviewStateS3():
    s3_state_json = _getAllCompletedJsonSuperS3__BETTER() # mocks/get_all_superS3__BETTER.py
    s3 = boto3.client('s3')
    key = env_varz.S3_OVERVIEW_STATE_JSON
    print("UPLOADING S3 OVERVIEW:")
    print("upload to: " + key)
    print(json.dumps(s3_state_json, default=lambda o: o.__dict__, indent=4))
    s3.put_object(Body=json.dumps(s3_state_json, default=lambda o: o.__dict__), Bucket=env_varz.BUCKET_NAME, Key=key)
    return json.loads(json.dumps(s3_state_json, default=lambda o: o.__dict__))


def uploadEachChannelsCompletedJson(completed_captions_list: list[Vod]): # /mocks/completed_captions_list.py
    s3 = boto3.client('s3')
    big_key_val_list = {}
    prepped_rel_data = {}

    for vod in completed_captions_list:
        if big_key_val_list.get(vod['channel']):
            big_key_val_list[vod['channel']].append(vod)
        else:
            big_key_val_list[vod['channel']] = []
            big_key_val_list[vod['channel']].append(vod)
    for chan in big_key_val_list:
        key = getIndivChannelKey(chan)
        print("UPLOADING COMPLETED LIST (caps + audio) for: " + chan)
        print("upload to: " + key)
        print(json.dumps(big_key_val_list[chan], indent=4))
        s3.put_object(Body=json.dumps(big_key_val_list[chan], default=lambda o: o.__dict__), Bucket=env_varz.BUCKET_NAME, Key=key)
    print("prepped_rel_data")
    print("prepped_rel_data")
    print("prepped_rel_data")
    print("prepped_rel_data")
    print("prepped_rel_data")
    print("prepped_rel_data")
    print(json.dumps(prepped_rel_data, indent=4))
    return big_key_val_list # /mocks/big_key_val_list.py

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
def _getAllCompletedJsonSuperS3__BETTER(): # -> mocks/getAllCompletedJsonSuperS3__BETTER.py
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