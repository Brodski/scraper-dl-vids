from controllers.yt_download import uploadAudioToS3, updateScrapeHistory
import controllers.seleniumController as seleniumController
import controllers.rankingController as rankingController
import mocks.initScrapData
import mocks.initHrefsData
import mocks.ytdlObjMetaDataList
import controllers.yt_download as yt
import datetime
import json
import boto3
# from flask import jsonify, abort



CURRENT_DATE_YMD = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
BUCKET_NAME = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket'
directory_name = 'mydirectory' # this directory legit exists in this bucket ^
directory_name_real = "channels/ranking/raw"
S3_ALREADY_DL_KEYBASE = 'channels/scrapped/'
S3_CAPTIONS_KEYBASE = 'channels/captions/'
# S3_ALREADY_DL_KEY = 'channels/scrapped/lolgeranimo/2023-04-01.json'


####################################################
# 1
def getTopChannelsAndSave():
    # Make http request to sullygnome. 3rd party website
    topChannels = rankingController.getTopChannels(numChannels=30) 

    # Saves those channels to S3 
    json_data = rankingController.saveTopChannels(topChannels) # json_data = /mocks/getTopChannelsAndSaveResponse.json

    relavent_data = rankingController.tidyData(json_data) # relavent_data = /mocks/initScrapData.py
    relavent_data = rankingController.addVipList(relavent_data) # same ^ but with gera
    initYtdlAudio(relavent_data, initYtdlAudio=False)
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
    vidLimit = 3 if isDebug else 10;
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
    print ()
    print ()
    print ()
    # Download X vids from Y channels
    # see /mocks/metadata_ytdl_list.txt
    metadata_Ytdl_list = yt.bigBoyChannelDownloader(scrapped_channels_with_todos, chnLimit=chnLimit, vidDownloadLimit=vidLimit)
    print("++++++++++++++++++++++++++++++++++")
    print("++++++++++++++++++++++++++++++++++")
    print("++++++++++++++++++++++++++++++++++")
    try:
        # print(json.dumps(metadata_Ytdl_list.__dict__))
        print(str(metadata_Ytdl_list.__dict__))
    except:
        print('    (initYtdlAudio) failed dump')

    print ("(initYtdlAudio) DOWNLOADED THESE:")
    for yt_meta in metadata_Ytdl_list:       
        print (   "(initYtdlAudio) - " + yt_meta.username + " @ " + yt_meta.metadata.get("title"))
    for yt_meta in metadata_Ytdl_list:        
        # SEND mp3 & metadata TO S3 --> channels/captions/<CHN>/<DATE>/<ID>.mp3
        isSuccess = uploadAudioToS3(yt_meta, isDebug) # key = upload 'location' in the s3 bucket 
        if isSuccess:
          updateScrapeHistory(yt_meta)  
        # UPDATE SCRAPE HISTORY
        # updateScrapeHistory(metadata)
        # UPDATE COMPLETED DOWNLOADS
        # updateCompletedDownloads(yt_meta, keybase)

        # Nope. Not here
        # yt.transcribefileWhisperAi(yt_meta) # (lolgeranimo, 12341234, {...})

        # print ("Creating caption: " + yt_meta.username + " -> " + yt_meta.link)

       
        # print ("KEY CAPTIONS=" + keybase)
        # isSuccess = uploadAudioToS3(metadata, keybase) # key = upload 'location' in the s3 bucket 


    # each_channels_and_their_ytdl_vids_metadata = mocks.ytdlObjMetaDataList.getYytdlObjMetadataList()
    # updateScrapeHistory(metaData_yt)
    return "done initYtdlAudio"
    return metadata_Ytdl_list
            
    if metaDownloads is None:
        print("failed to download: " + channel['displayname'])
            # abort(400, description="Failed to download: href_channel_list[0]['twitchurl']")
    return metaDownloads

def updateSpider():
    s3 = boto3.client('s3')
    # TODO env var this Prefix
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_CAPTIONS_KEYBASE)['Contents']
    # sorted_objects = sorted(objects, key=lambda obj: obj['LastModified'])
    sorted_objects = sorted(objects, key=lambda obj: obj['Key'])
    print("-----SORTED (OFFICIAL)---- ")
    keyPathList = []
    # channel = Array<vods> vods
    # poopy = channels: [
    #                     {   
    #                         channel_name: "name",
    #                         vods_uploaded: [123, 111,222,...]
    #                     }
    #                 ],
    allOfit = {}
    for obj in sorted_objects:
        print("Key= " + f"{obj['Key']} ----- Last modified= {obj['LastModified']}")
        # print("ContinuationToken: " +     str(obj.get('ContinuationToken')))
        # print("NextContinuationToken: " + str(obj.get('NextContinuationToken')))
        keyPathList.append(obj['Key'])
        temp = str(obj['Key']).split(S3_CAPTIONS_KEYBASE, 1)[1]  #obj[key] = channels/captions/lolgeranimo/5057810/Calculated-v5057810.mp3
        channel, vod_id = temp.split("/", 2)[:2]
        print(channel + " --- " + vod_id)
        if allOfit.get(channel):
            allOfit[channel].append(vod_id)
        else:
            allOfit[channel] = [vod_id]
    print ("allOfit")
    print (allOfit)

    return 'gg'