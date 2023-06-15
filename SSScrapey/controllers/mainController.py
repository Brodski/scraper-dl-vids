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
from flask import abort

import env_app as env_varz


####################################################
# 1
def getTopChannelsAndSave():
    # Make http request to sullygnome. 3rd party website
    topChannels = rankingController.getTopChannels(numChannels=30) 

    # Saves those channels to S3 
    # json_data = rankingController.saveTopChannels(topChannels) # json_data = /mocks/getTopChannelsAndSaveResponse.json

    # relavent_data = rankingController.tidyData(json_data) # relavent_data = /mocks/initScrapData.py
    relavent_data = rankingController.tidyData(topChannels) # relavent_data = /mocks/initScrapData.py
    relavent_data = rankingController.addVipList(relavent_data) # same ^ but with gera
    initYtdlAudio(relavent_data, isDebug=True)
    return relavent_data
    # return json_data
####################################################

####################################################
# 2                                                #
# IntializeScrape                                  #
# WE CAN PROB IGNORE THIS                          
# THIS IS JUST FOR THST CHECKY "GET FEW BEFORE"
def getChannelFromS3(): # -> return data = getTopChannelsAndSave() = json_data
    # We first get the key/paths from the s3
    sorted_s3_paths =  rankingController.preGetChannelInS3AndTidy() # returns a List[str] of S3 Keys/Paths that point to the save s3 channels:
    combined_channels_list = rankingController.getChannelInS3AndTidy(sorted_s3_paths) # returns a List[{dict}] of channels and culled date
    combined_channels_list = rankingController.addVipList(combined_channels_list) # ^ but with gera
    # Returns: 
        #     {
        #     "displayname": "LoLGeranimo",
        #     "language": "English",
        #     "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
        #     "twitchurl": "https://www.twitch.tv/lolgeranimo",
        #     "url": "lolgeranimo"
        #   },...,
    return combined_channels_list
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
    chnLimit = 3 if isDebug else 99;
    vidLimit = 3 if isDebug else 5;
    if isDebug:
        print("    (initYtdlAudio) Getting mock channels")
        scrapped_channels = mocks.initHrefsData.getHrefsData()
    else:
        print("    (initYtdlAudio) Getting IRL channels ")
        scrapped_channels = seleniumController.scrape4VidHref(channels, True) # returns /mocks/initHrefsData.py

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
    # see /mocks/metadata_ytdl_list.txt
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
    syncAudioFilesUploadJsonS3()
    print("COMPLEEEEEEEEEEEEEEEEEETE")
    return "Compelte init"





# could polish these 2 (4) methods
# this method is kinda shit and hacky
def _appendCaptionJson(channel, vod):
    print("_appendCaptionJson: " + channel + " - " + vod)

def syncCaptionsUploadJsonS3():
    allOfIt = _getCompletedJsonSuperS3() # allOfIt = /mocks/completedCaptionsJson.py
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
    print(allOfIt)
    print(type(allOfIt))
    print('===')
    completed = {}
    captions_expected = [".vtt", ".json"]
    for chn_key, vod_dicts_value in allOfIt.items():
        print(chn_key + ": " + str(vod_dicts_value))
        print(chn_key + ": " + str(type(vod_dicts_value)))
        for vod_id, vods_data in vod_dicts_value.items():
            print('8888888888888')
            print(vod_id + ": " + str(vods_data))
            found = any('.vtt' in element[-4:] for element in vods_data)
            if (found):
                _appendCaptionJson(chn_key, vod_id)
                if completed.get(chn_key):
                    completed[chn_key].add(vod_id)
                else:
                    completed[chn_key] = { vod_id }
            # for file_type in captions_expected:
                # found = any((file_type in element[-5:] and element != "metadata.json" ) for element in vods_data)
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print("i want it all")
    print(completed)
    # return str(completed)
    s3 = boto3.client('s3')
    if completed is None or len(completed)==0:
        abort(400, description="Something is wrong with 'uploaded' caption json file")
    try:
        s3.put_object(Body=str(completed), Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_CAPTIONS_UPLOADED)
        return str(completed)
    except:
        abort(400, description="Failed to do caption sync")

def syncAudioFilesUploadJsonS3():
    allOfIt = _getUploadedAudioS3() # allOfIt = /mocks/completedAudioJson.py
    s3 = boto3.client('s3')
    if allOfIt is None or len(allOfIt)==0:
        abort(400, description="Something is wrong with 'uploaded' audio json file")
    try:
        print()
        print()
        print()
        print()
        print(" :) ")
        # print(allOfIt)
        # print(type(allOfIt))
        # print(str(json.dumps(allOfIt)))
        s3.put_object(Body=str(allOfIt), Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_AUDIO_UPLOADED)
        return str(allOfIt)
    except:
        abort(400, description="Failed to do audio sync")
        

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
def _getCompletedJsonSuperS3():
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket=env_varz.BUCKET_NAME, Prefix=env_varz.S3_CAPTIONS_KEYBASE)['Contents']
    sorted_objects = sorted(objects, key=lambda obj: obj['Key'])
    print("----- _getCompletedJsonSuperS3 ---- ")
    
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
        if allOfIt.get(channel):
            print('        ass=' + str(allOfIt.get(channel).get(vod_id)))
            if allOfIt.get(channel).get(vod_id): # if vod_id for channel exists
                print("      ??? " + str(type(allOfIt.get(channel))))
                allOfIt.get(channel).get(vod_id).append(filename)
            else: # else create a list that has all filenames
                allOfIt.get(channel)[vod_id] = [filename]
                print ('                pooooooooooooooooooooooooooooop')
                print ('                pooooooooooooooooooooooooooooop')
                print (type(allOfIt.get(channel)[vod_id] ))
        else:
            print ('---bang')
            vod_dict = { vod_id: [filename] }
            allOfIt[channel] = vod_dict
    print ()
    print (allOfIt)
    print ()
    print ("420")
    for key, value in allOfIt.items():
        print(key + ": " + str(value))
    
    return allOfIt

def _getUploadedAudioS3():
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket=env_varz.BUCKET_NAME, Prefix=env_varz.S3_CAPTIONS_KEYBASE)['Contents']
    sorted_objects = sorted(objects, key=lambda obj: obj['Key'])
    print("----- _getUploadedAudioS3 ---- ")
    
    allOfIt = {}
    for obj in sorted_objects:
        print("Key= " + f"{obj['Key']}")

        # print("ContinuationToken: " +     str(obj.get('ContinuationToken')))
        # print("NextContinuationToken: " + str(obj.get('NextContinuationToken')))

        # 1. obj[key] = channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3
        # 2. temp = lolgeranimo/5057810/Calculated-v5057810.mp3
        # 3. channel, vod_i = [ lolgeranimo, 5057810 ] 
        temp = str(obj['Key']).split(env_varz.S3_CAPTIONS_KEYBASE, 1)[1]   # 2
        channel, vod_id = temp.split("/", 2)[:2] # 3 
        if allOfIt.get(channel):
            allOfIt[channel].add(vod_id)
        else:
            allOfIt[channel] = {vod_id}
    print ()
    print ("allOfIt:")
    print ()
    print (allOfIt)
    print ()
    for key, value in allOfIt.items():
        print(key + ": " + str(value))
    
    # allOfIt = { lck: {'576354726'}, lolgeranimo: {'5057810', '28138895'} }
    return allOfIt