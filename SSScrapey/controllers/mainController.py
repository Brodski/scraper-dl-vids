import urllib
from controllers.yt_download import uploadAudioToS3
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
from flask import abort, jsonify

import env_app as env_varz

import ast

####################################################
# 1
def getTopChannelsAndSave(isDebug=False):
    # Make http request to sullygnome. 3rd party website
    topChannels = rankingController.getTopChannels(numChannels=30) 

    # Saves those channels to S3 
    # json_data = rankingController.saveTopChannels(topChannels) # json_data = /mocks/getTopChannelsAndSaveResponse.json
    # relavent_data = rankingController.tidyData(json_data) # relavent_data = /mocks/initScrapData.py
    relavent_data = rankingController.tidyData(topChannels) # relavent_data = /mocks/initScrapData.py
    relavent_data = rankingController.addVipList(relavent_data) # same ^ but with gera
    if isDebug:
        print ("ENDING PREMPTIVELY B/C is DEBUG")
        return relavent_data
    initYtdlAudio(relavent_data, isDebug=True)
    return "!!!"
####################################################

####################################################
# 2                                                #
# IntializeScrape                                  #
# WE CAN PROB IGNORE THIS                          
# THIS IS JUST FOR THST CHECKY "GET FEW BEFORE"
def getChannelFromS3(): # -> return data = getTopChannelsAndSave() = json_data
    return "COMMENTED OUT CODE!!! junk"
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
        scrapped_channels = seleniumController.scrape4VidHref(channels, isDebug) # returns /mocks/initHrefsData.py
        
    print("     (initYtdlAudio) scrapped_channels")
    print("     (initYtdlAudio) " + str(scrapped_channels))
    scrapped_channels_with_todos = yt.addTodoListS3(scrapped_channels)  # scrapped_channels == scrapped_channels_with_todos b/c pass by ref
    # scrapped_channels_with_todos -> returns: [ {
    #   'displayname': 'LoLGeranimo', 
    #   'url': 'lolgeranimo', 
    #   'links': ['/videos/5057810', '/videos/28138895'], 
    #   'todos': ['/videos/5057810', '/videos/28138895']
    #  }, {
    #     ...
    #   }
    # ]
    print ("     (initYtdlAudio) scrapped_channels_with_todos=")
    print (str(scrapped_channels_with_todos))
    # Download X vids from Y channels
    # -> /mocks/metadata_ytdl_list.txt
    chnLimit = 3 if isDebug else 99;
    vidLimit = 1 if isDebug else 2;
    metadata_Ytdl_list = yt.bigBoyChannelDownloader(scrapped_channels_with_todos, chnLimit=chnLimit, vidDownloadLimit=vidLimit)
    print("     (initYtdlAudio) ++++++++++++++++++++++++++")
    print("     (initYtdlAudio) ++++++++++++++++++++++++++")
    print("     (initYtdlAudio) ++++++++++++++++++++++++++")
    try:
        print(str(metadata_Ytdl_list[0]))
        # print(str( json.dumps(metadata_Ytdl_list, default= lambda m: m.__dict__)))
    except:
        print('    (initYtdlAudio) failed dump')
        print('    (initYtdlAudio) failed dump')
        print('    (initYtdlAudio) failed dump')
    print ("(initYtdlAudio) DOWNLOADED THESE:")
    print (metadata_Ytdl_list)
    for yt_meta in metadata_Ytdl_list:       
        print (   "(initYtdlAudio) - " + yt_meta.channel + " @ " + yt_meta.metadata.get("title"))
    for yt_meta in metadata_Ytdl_list:        
        # SEND mp3 & metadata TO S3 --> channels/vod-audio/<CHN>/<DATE>/<ID>.mp3
        isSuccess = uploadAudioToS3(yt_meta, isDebug) # key = upload 'location' in the s3 bucket 
    # return ":)"
    # UPDATE SCRAPE HISTORY
    # updateScrapeHistory(metadata)

    # UPDATE COMPLETED DOWNLODS
    # syncAudioFilesUploadJsonS3()
    createCaptionTodoList4Whispher()
    print("COMPLEEEEEEEEEEEEEEEEEETE")
    return "Compelte init"



def createCaptionTodoList4Whispher(isDebug=False):
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    print('zzzzzz           createCaptionTodoList4Whispher         zzzzzzz')
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    # allOfIt_ids, allOfIt_titles = _getCompletedAudioJsonSuperS3() # lotsOfData = mocks/completedJsonSuperS3.py
    allOfIt = _getAllCompletedJsonSuperS3__BETTER() # lotsOfData = mocks/completedJsonSuperS3.py
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')

    if allOfIt is None or len(allOfIt)==0:
        abort(400, description="Something is wrong with '_getCompletedAudioJsonSuperS3' audio json file")
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
                print("MISSING CAPTIONS")
                print(k_chn + " " + id)
                vod = Vod(channel=k_chn, id=id, title=vod_title)
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



# could polish these 2 (4) methods
# this method is kinda shit and hacky
def syncCaptionsUploadJsonS3():
    return "COMMENTED OUT CODE, NOT NEEDED!!"
    # lotsOfAudio = _getCompletedAudioJsonSuperS3() # allOfIt = /mocks/completedJsonSuperS3.py
    # print('qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq')
    # print('qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq')
    # print('qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq')
    # print(lotsOfAudio)
    # print (json.dumps(lotsOfAudio, default=lambda o: o.__dict__))
    # print('===')
    # completed = {}
    # captions_expected = [".vtt", ".json"]
    # for audio in lotsOfAudio:
    #     print('9090909090909')
    #     print (json.dumps(audio, default=lambda o: o.__dict__))
    # for chn_key, vod_dicts_value in lotsOfAudio.items():
    #     print(chn_key + ": " + str(vod_dicts_value))
    #     for vod_id, vods_data in vod_dicts_value.items():
    #         vod_id = int(vod_id)
    #         print('8888888888888')
    #         print(str(vod_id) + ": " + str(vods_data))
    #         found = any('.vtt' in element[-4:] for element in vods_data)
    #         if (found):
    #             if completed.get(chn_key) and vod_id not in completed.get(chn_key):
    #                 completed[chn_key].append(vod_id)
    #             elif not completed.get(chn_key):
    #                 completed[chn_key] = [ vod_id ]
    #         # for file_type in captions_expected:
    #             # found = any((file_type in element[-5:] and element != "metadata.json" ) for element in vods_data)
    # print()
    # print()
    # print()
    # print()
    # print()
    # print()
    # print()
    # print()
    # print("i want it all")
    # print(completed)
    # print("json.dumps(completed)")
    # print(json.dumps(completed))
    # # return str(completed)
    # return "lol"
    # s3 = boto3.client('s3')
    # if completed is None or len(completed)==0:
    #     abort(400, description="Something is wrong with 'uploaded' caption json file")
    # try:
    #     s3.put_object(Body=json.dumps(completed), Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_CAPTIONS_UPLOADED)
    #     return str(completed)
    # except:
    #     abort(400, description="Failed to do caption sync")

def syncAudioFilesUploadJsonS3():
    return "COMMENTED OUT CODE RIP!"
    # print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    # print('zzzzzz           syncAudioFilesUploadJsonS3         zzzzzzz')
    # print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    # # allOfIt_ids, allOfIt_titles = _getCompletedAudioJsonSuperS3() # lotsOfData = mocks/completedJsonSuperS3.py
    # allOfIt = _getAllCompletedJsonSuperS3__BETTER() # lotsOfData = mocks/completedJsonSuperS3.py
    # print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    # print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')

    # if allOfIt is None or len(allOfIt)==0:
    #     abort(400, description="Something is wrong with '_getCompletedAudioJsonSuperS3' audio json file")
    # print ("lotsOfAudio")
    # print (lotsOfAudio)
    # print (json.dumps(lotsOfAudio, default=lambda o: o.__dict__,))
    # print()
    # print()
    # print()
    # print()
    # print(" :) ")
    # print(allOfIt)
    # print(type(allOfIt))
    # print(json.dumps(allOfIt))
    # print()
    # print()
    # print()
    # print(json.dumps(allOfIt_titles))
    # lotsOfAudio = []
    # for k_chn, v_idz in allOfIt_ids.items():
    #     print(k_chn)
    #     print(v_idz)
    #     audio = AudioResponse()
    #     audio.channel = k_chn
    #     audio.vod_ids = v_idz
    #     # audio.vod_titles = allOfIt_titles.get(k_chn)
    #     lotsOfAudio.append(audio)
    # s3 = boto3.client('s3')
    # s3.put_object(Body=json.dumps(allOfIt_ids), Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_AUDIO_UPLOADED)
    # return str(allOfIt_ids)
        

def getAllFilesS3(isDebug=False): # -> mocks/allFilesS33333.py
    return "COMMENTED OUT METHOD"
#     allOfIt = _getAllCompletedJsonSuperS3__BETTER()
#     print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
#     print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
#     print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
#     print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
#     print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
#     print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
#     print(allOfIt)
#     vodS3_set = []
#     print("looping")
#     for k_channel, vod_dict in allOfIt.items():
#         vodS3_res = VodS3Response()
#         vodS3_res.channel = k_channel

#         vodS3_set[k_channel] = vodS3_res
#         for k_vodId, v_files in vod_dict.items():
#             print ('-')
#             print(k_vodId)
#             print(v_files)
#             vodS3_res.vod_files[k_vodId] = v_files
            
#     print("vvvvvvvvvvvvvvvvvvvvvv")
#     print(vodS3_set)
#     print()
#     print(json.dumps(vodS3_set, default=lambda o: o.__dict__, indent=4))
#     if isDebug:
#         return json.loads(json.dumps(vodS3_set, default=lambda o: o.__dict__))
#     return vodS3_set

def getUploadedAudioS3():
    return "COMMENTED OUT COOOOODE!"
    # vodS3_set = getAllFilesS3() # -> mocks/allFilesS33333.py
    # print("22222222222222222222222222222222")
    # captions_ext = ['.json', '.vtt']
    # # audio_without_caps = List[VodS3Response]
    # audio_without_caps = VodS3Response
    # for k_channel, vod_s3_res in vodS3_set.items():
    #     print()
    #     print(k_channel)
    #     print("vod_s3_res.vod_files")
    #     # print(vod_s3_res.vod_files)
    #     print(json.dumps( vod_s3_res.vod_files,  indent=4))
    #     print(type(vod_s3_res.vod_files))
    #     for id, vod_files in vod_s3_res.vod_files.items():
    #         print("id: " + str(id))
    #         print("vod_file: " + str(vod_files))
    #         for file in vod_files:
    #             print("    " + str(file))
    #             if file[-5:] not in captions_ext and file[-4:] not in captions_ext and file != "metadata.json":
    #                 # audio_without_caps.append({"id": k_vodId, "title": file})
    #                 print("---- " + k_channel)
    #                 print("---- " + (file))
    #                 audio_without_caps.append(VodS3Response(channel=k_channel, vod_files={id: [file] }))
    #                 #HERE
    #                 #HERE
    #                 #HERE
    #                 #HERE
    #                 #HERE
    #                 #HERE
    #                 #HERE
    #                 #HERE
    #                 #HERE
    #                 #HERE
    #                 #HERE
    # print("audio_without_caps")
    # print("audio_without_caps")
    # print("audio_without_caps")
    # print(audio_without_caps)
    # print(json.dumps( audio_without_caps,  indent=4, default=lambda o: o.__dict__))
    # return "yes!"


def _getCompletedAudioJsonSuperS3(isDebug=False): # -> lotsOfData = mocks/completedJsonSuperS3.py
    return "MORE COMMENTED OUT CODE!!!"
    # s3 = boto3.client('s3')
    # objects = s3.list_objects_v2(Bucket=env_varz.BUCKET_NAME, Prefix=env_varz.S3_CAPTIONS_KEYBASE)['Contents']
    # sorted_objects = sorted(objects, key=lambda obj: obj['Key'])
    # print("----- _getCompletedAudioJsonSuperS3 ---- ")
    
    # allOfIt_ids = {}
    # allOfIt_titles = {}
    # for obj in sorted_objects:
    #     print("===================================")
    #     print("Key= " + f"{obj['Key']}")

    #     # print("ContinuationToken: " +     str(obj.get('ContinuationToken')))
    #     # print("NextContinuationToken: " + str(obj.get('NextContinuationToken')))

    #     # 1. obj[key] = channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3
    #     # 2. temp = lolgeranimo/5057810/Calculated-v5057810.mp3
    #     # 3. channel, vod_i = [ lolgeranimo, 5057810 ] 
    #     temp = str(obj['Key']).split(env_varz.S3_CAPTIONS_KEYBASE, 1)[1]   # 2
    #     channel, vod_id, vod_title = temp.split("/", 2)[:3] # 3 
    #     vod_id = int(vod_id)
    #     if vod_title[-5:] == ".json" or vod_title[-4:] == ".vtt":
    #         continue
    #     print ("vod_id=" + str(vod_id) + " --- allOfIt.get(channel)=" + str(allOfIt_ids.get(channel)))
    #     if allOfIt_ids.get(channel) and vod_id not in allOfIt_ids.get(channel):
    #         print(vod_id)
    #         allOfIt_ids[channel].append({vod_id: vod_title})
    #         allOfIt_titles[channel].append(vod_title)
    #     elif not allOfIt_ids.get(channel):
    #         allOfIt_ids[channel] = [{vod_id: vod_title}]
    #         allOfIt_titles[channel] = [vod_title]
    # print ()
    # print ("allOfIt:")
    # print ()
    # print (allOfIt_ids)
    # print ()
    # print ()
    # print ()
    # print ('ids')
    # for key, value in allOfIt_ids.items():
    #     print(key + ": " + str(value))
    # print ()
    # print ()
    # print ()
    # print ('titles')
    # for key, value in allOfIt_titles.items():
    #     print(key + ": " + str(value))
    
    # print ()
    # print ()
    # print ()
    # print ()
    # print ()
    # # allOfIt = { lck: {'576354726'}, lolgeranimo: {'5057810', '28138895'} }

    # if allOfIt_ids is None or len(allOfIt_ids)==0:
    #     abort(400, description="Something is wrong with '_getCompletedAudioJsonSuperS3' audio json file")
    # print()
    # print()
    # print()
    # print()
    # print(" :) ")
    # print(allOfIt_ids)
    # print(type(allOfIt_ids))
    # print(json.dumps(allOfIt_ids, indent=4))
    # print()
    # print()
    # print()
    # print(json.dumps(allOfIt_titles,indent=4))
    # lotsOfAudio = []
    # for k_chn, v_idz in allOfIt_ids.items():
    #     print(k_chn)
    #     print(v_idz)
    #     audio = AudioResponse()
    #     audio.channel = k_chn
    #     audio.vod_ids = v_idz
    #     # audio.vod_titles = allOfIt_titles.get(k_chn)
    #     lotsOfAudio.append(audio)
    # if isDebug:
    #     print( json.dumps(lotsOfAudio, default=lambda o: o.__dict__, indent=4) )
    #     return json.dumps(lotsOfAudio, default=lambda o: o.__dict__)
    # return lotsOfAudio # lotsOfData = mocks/completedJsonSuperS3.py