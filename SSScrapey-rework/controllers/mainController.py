import urllib

import controllers.seleniumController as seleniumController
import controllers.createToDoController as createToDoController
import controllers.databaseController as databaseController
import controllers.MicroDownloader.downloader as downloader
import controllers.MicroTranscriber.transcriber as transcriber
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
    topChannels = createToDoController.getTopChannels() 
    
    scrapped_channels: List[ScrappedChannel] = createToDoController.instantiateJsonToClassObj(topChannels) # relevant_data = /mocks/initScrapData.py
    scrapped_channels: List[ScrappedChannel]  = createToDoController.addVipList(scrapped_channels) # same ^ but with gera
    if isDebug:
        scrapped_channels: List[ScrappedChannel] = mocks.initHrefsData.getHrefsData()
        # print(json.dumps(scrapped_channels, default=lambda o: o.__dict__, indent=4))
    else:
        scrapped_channels: List[ScrappedChannel] = seleniumController.scrape4VidHref(scrapped_channels, isDebug) # returns -> /mocks/initHrefsData.py

    databaseController.updateDb1(scrapped_channels)
    return "done'"

    # doUploadStuff(scrapped_channels, metadata_Ytdl_list)

    return "Finished kickit()"

#####################################################
#
#       Microservice 2
#
#####################################################

def kickDownloader(isDebug=False):
    vods_list: List[Vod] = downloader.getTodoFromDatabase(isDebug=isDebug) # limit = 5
    vod: Vod = downloader.getNeededVod(vods_list)
    if isDebug:
        vod = Vod("40792901", "nmplol", "todo", -1, "-1") # (Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
    print("doing this vod:")
    print(vod.print())
    downloaded_metadata = downloader.downloadTwtvVid2(vod, True)
    if downloaded_metadata == "403":
        downloader.updateUnauthorizedVod(vod)
        return "nope gg sub only"
    downloaded_metadata = downloader.removeNonSerializable(downloaded_metadata)
    downloaded_metadata, outfile = downloader.convertVideoToSmallAudio(downloaded_metadata)
    isSuccess = downloader.uploadAudioToS3_v2(downloaded_metadata, outfile, vod)
    if (isSuccess):
        downloader.updateVods_Round2Db(downloaded_metadata, vod.id)
    return downloaded_metadata


#####################################################
#
#       Microservice 3
#
#####################################################

def kickWhisperer():
    transcriber.kickIt()
    return "kick whisperer"

####################################################

def kickit_just_gera(isDebug=False):
    relevant_data = createToDoController.addVipList([]) # same ^ but with gera
    metadata_Ytdl_list = initYtdlAudio(relevant_data, isDebug=isDebug) # relevant_data = data from gnome api
    if len(metadata_Ytdl_list) == 0:
        print("NOTHING TO DO metadata_Ytdl_list is empty")
        return "NOTHING TO DO metadata_Ytdl_list is empty"
    doUploadStuff(relevant_data, metadata_Ytdl_list)
    print("JUST GERA DONE!")
    return "JUST GERA DONE!"

def doUploadStuff(relevant_data, metadata_Ytdl_list):
    for yt_meta in metadata_Ytdl_list:
        yt.uploadAudioToS3(yt_meta) 
        
        data_custom = createCustomMetadata(yt_meta)
        upload_custom_metadata(data_custom)
    
    allOfIt = _getAllCompletedJsonSuperS3__BETTER() # lotsOfData = mocks/get_all_superS3__BETTER.py.py
    [missing_captions_list, completed_captions_list] = uploadTodoAndCompletedJsons(allOfIt)
    uploadOverviewStateS3(allOfIt)
    each_completed_big_kv_list = uploadEachChannelsCompletedJson(completed_captions_list)
    uploadLightOverviewS3(each_completed_big_kv_list, relevant_data)

#####################################################
#                                                   #
#                                                   #
# calls yt.addTodoDownlaods(channels)
# calls yt.scrape4VidHref(^)
# calls yt.addTodoListS3(^)
def initYtdlAudio(scrapped_channels:List[ScrappedChannel], *, isDebug=False):
    print ("00000000000000                 00000000000000000")
    print ("00000000000000  initYtdlAudio  00000000000000000")
    print ("00000000000000                 00000000000000000")

    # if isDebug:
    #     scrapped_channels = mocks.initHrefsData.getHrefsData()
    # else:
    #     scrapped_channels = seleniumController.scrape4VidHref(channels, isDebug) # returns -> /mocks/initHrefsData.py

    print ("     (initYtdlAudio) scrapped_channels  =" + str(scrapped_channels))
    # THIS IS FUCKED TODO
    scrapped_channels_with_todos = yt.addTodoListS3(scrapped_channels)  # returns -> /mocks/scrapped_channels_with_todos.py
    print ("     (initYtdlAudio) scrapped_channels_with_todos size =" + str(len(scrapped_channels_with_todos)))

    # Download X vids from Y channels
    metadata_Ytdl_list: List[Metadata_Ytdl] = yt.bigBoyChannelDownloader(scrapped_channels_with_todos, isDebug=isDebug)
    print("     (initYtdlAudio) ++++++++++++++++++++++++++")
    print("     (initYtdlAudio) ++++++++++++++++++++++++++")
    print("     (initYtdlAudio) ++++++++++++++++++++++++++")
    print("     (initYtdlAudio) DOWNLOADED THESE:")
    for yt_meta in metadata_Ytdl_list:
        print (   "(initYtdlAudio) - " + yt_meta.channel + " @ " + yt_meta.metadata.get("title"))
    # if isDebug:
    #     return json.dumps(metadata_Ytdl_list, default=lambda o: o.__dict__)
    return metadata_Ytdl_list

def upload_custom_metadata(data_custom):
    print ("00000000000000                         00000000000000000")
    print ("00000000000000  upload_custom_metadata 00000000000000000")
    print ("00000000000000                         00000000000000000")
    
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
    custom_metadata_json_file[vod_id] = vod_metadata
    
    print("custom_metadata")
    print("custom_metadata")
    print("custom_metadata")
    print("custom_metadata")
    print(json.dumps(custom_metadata_json_file , indent=4))
    s3.put_object(Body=json.dumps(custom_metadata_json_file, default=lambda o: o.__dict__), ContentType="application/json; charset=utf-8", Bucket=env_varz.BUCKET_NAME, Key=key)

    return 'done X'


def createCustomMetadata(yt_meta: Metadata_Ytdl): # modks/ytdlSingleVidMetaData
    print("yt_meta")
    print("yt_meta")
    print(json.dumps(yt_meta.__dict__, indent=4))
    data = {
        'id': yt_meta.metadata.get("id")[1:] if yt_meta.metadata.get("id") else "",
        'channel': yt_meta.channel,
        "display_title": yt_meta.metadata.get("title"),
        "duration": yt_meta.metadata.get("duration"),
        "thumbnail": yt_meta.metadata.get("thumbnail"),
        "display_title": yt_meta.metadata.get("title"),
        "timestamp": yt_meta.metadata.get("timestamp"),
        "view_count": yt_meta.metadata.get("view_count"),
        "upload_date": yt_meta.metadata.get("upload_date"),
        "duration_string": yt_meta.metadata.get("duration_string"),
        "epoch": yt_meta.metadata.get("epoch"),
        "fulltitle": yt_meta.metadata.get("fulltitle"),
        "logo": yt_meta.logo
    }

    print("data")
    print("data")
    print("data")
    print("data")
    print("data")
    print(data)
    print(yt_meta.logo)
    return data



# could be better
def uploadTodoAndCompletedJsons(allOfIt, isDebug=False):
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    print('zzzzzz        uploadTodoAndCompletedJsons        zzzzzzz')
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')

    if allOfIt is None or len(allOfIt)==0:
        raise Exception("Something is wrong with '_getCompletedAudioJsonSuperS3' audio json file")

    captions_ext = ['.json', '.vtt', '.txt']
    missing_captions_list = []
    completed_captions_list = []

    for k_chn, v_id_files in allOfIt.items():
        for id, files in v_id_files.items():
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
    print("Uploading completed_captions_list ----> " + env_varz.S3_COMPLETED_CAPTIONS_JSON)
    print("Uploading todo (missing_captions_list) ----> " + env_varz.S3_COMPLETED_TODO_AUDIO)
    s3.put_object(Body=json.dumps(missing_captions_list, default=lambda o: o.__dict__),   ContentType="application/json; charset=utf-8", Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_TODO_AUDIO)
    s3.put_object(Body=json.dumps(completed_captions_list, default=lambda o: o.__dict__), ContentType="application/json; charset=utf-8", Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_CAPTIONS_JSON)

    # if isDebug and os.getenv("ENV") == "local":
    #     return json.loads(json.dumps({"completed_captions_list": completed_captions_list, "missing_captions_list": missing_captions_list}, default=lambda o: o.__dict__))
    return [missing_captions_list, completed_captions_list]

def getIndivChannelKey(chan):
    return env_varz.S3_COMPLETED_INDIV_CHAN_ROOT + chan + ".json"

# returns -> /mocks/light_overview_s3.py
def uploadLightOverviewS3(each_completed_big_kv_list, relevant_data): # /mocks/each_completed_big_kv_list_each_complete.py
    print ("00000000000000                        00000000000000000")
    print ("00000000000000  uploadLightOverviewS3 00000000000000000")
    print ("00000000000000                        00000000000000000")
    # prepped_rel_data = {'lolgeranimo': '-1', 'ibai': 1, 'kaicenat': 2, 'fextralife': 3, 'kingsleague': 4, 'loud_coringa': 5, 'cellbit': 6, 'k3soju': 7, 'handongsuk': 8, 'eliasn97': 9, 'tarik': 10, 'xqc': 11, 'gaules': 12, 'hasanabi': 13, 'paulinholokobr': 14, 'ironmouse': 15, 'nix': 16, 'otplol_': 17, 'esl_dota2': 18, 'fps_shaka': 19, 'paragon_dota': 20}
    prepped_rel_data = {} 
    for chan in relevant_data:
        print(chan.get("url"))
        # print(chan)
        prepped_rel_data[chan.get("url")] = {}
        prepped_rel_data[chan.get("url")] = {
            "current_rank": chan.get("current_rank"),
            "logo": chan.get("logo"),
            "twitchurl": chan.get("twitchurl"),
            "displayname": chan.get("displayname")
        }

    light_overview_list = []
    for chan in each_completed_big_kv_list:
        print()
        rnum = None
        twitchurl = None
        displayname = None
        logo = None
        chanx = prepped_rel_data.get(chan)
        print(chanx)
        if chanx:
            rnum = chanx.get("current_rank")
            twitchurl = chanx.get("twitchurl")
            displayname = chanx.get("displayname")
            logo = chanx.get("logo")
        light_overview_list.append({
            "channel": chan,
            "size": len(each_completed_big_kv_list[chan]),
            "path": getIndivChannelKey(chan),
            "current_rank": rnum if rnum else "9999",
            "twitchurl": twitchurl,
            "displayname": displayname,
            "logo": logo
        })
    s3 = boto3.client('s3')
    key = env_varz.S3_OVERVIEW_STATE_LIGHT_JSON
    print("UPLOADING LIGHTWEIGHT S3 OVERVIEW:")
    print("upload to: " + key)
    print(json.dumps(light_overview_list, default=lambda o: o.__dict__, indent=4))
    s3.put_object(Body=json.dumps(light_overview_list, default=lambda o: o.__dict__), ContentType="application/json; charset=utf-8", Bucket=env_varz.BUCKET_NAME, Key=key)
    return json.loads(json.dumps(light_overview_list, default=lambda o: o.__dict__))



def uploadOverviewStateS3(s3_state_json):
    print ("00000000000000                        00000000000000000")
    print ("00000000000000  uploadOverviewStateS3 00000000000000000")
    print ("00000000000000                        00000000000000000")
    s3 = boto3.client('s3')
    key = env_varz.S3_OVERVIEW_STATE_JSON
    print("UPLOADING S3 OVERVIEW:")
    print("upload to: " + key)
    print(json.dumps(s3_state_json, default=lambda o: o.__dict__, indent=4))
    s3.put_object(Body=json.dumps(s3_state_json, default=lambda o: o.__dict__), ContentType="application/json; charset=utf-8", Bucket=env_varz.BUCKET_NAME, Key=key)
    return json.loads(json.dumps(s3_state_json, default=lambda o: o.__dict__))


def uploadEachChannelsCompletedJson(completed_captions_list: list[Vod]): # /mocks/completed_captions_list.py
    print ("00000000000000                                   00000000000000000")
    print ("00000000000000  uploadEachChannelsCompletedJson  00000000000000000")
    print ("00000000000000                                   00000000000000000")
    s3 = boto3.client('s3')
    each_completed_big_kv_list = {}
    print("completed_captions_list")
    print(completed_captions_list)
    print()
    print()
    print()
    for vod in completed_captions_list:
        if each_completed_big_kv_list.get(vod.channel):
            each_completed_big_kv_list[vod.channel].append(vod)
        else:
            each_completed_big_kv_list[vod.channel] = []
            each_completed_big_kv_list[vod.channel].append(vod)
    for chan in each_completed_big_kv_list:
        key = getIndivChannelKey(chan)
        print("UPLOADING COMPLETED LIST (caps + audio) for: " + chan)
        print("upload to: " + key)
        print(json.dumps(each_completed_big_kv_list[chan], indent=4, default=lambda o: o.__dict__))
        s3.put_object(Body=json.dumps(each_completed_big_kv_list[chan], default=lambda o: o.__dict__),  ContentType="application/json; charset=utf-8", Bucket=env_varz.BUCKET_NAME, Key=key)
    return each_completed_big_kv_list # /mocks/each_completed_big_kv_list.py

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
        # print("@@@@@@@@@@@@@@@@@@@@@")
        # print("Key= " + f"{obj['Key']}")
        # print("channel: " +  (channel))     
        # print("vod_id: " +  (vod_id))
        # print("filename: " + (filename))
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




