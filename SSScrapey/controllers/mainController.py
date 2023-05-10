import controllers.videoHrefController as videoHrefController
import controllers.rankingController as rankingController
import mocks.initScrapData
import mocks.initHrefsData
import mocks.ytdlObjMetaDataList
import controllers.yt_download as yt
import datetime
# from flask import jsonify, abort



S3_CAPTIONS_KEYBASE = 'channels/captions/'
CURRENT_DATE_YMD = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")



####################################################
# 1
def getTopChannelsAndSave():
    # Make http request to sullygnome. 3rd party website
    topChannels = rankingController.getTopChannels(numChannels=30) 

    # Saves those channels to S3 
    json_data = rankingController.saveTopChannels(topChannels) # json_data = /mocks/getTopChannelsAndSaveResponse.json

    relavent_data = rankingController.tidyData(json_data) # relavent_data = /mocks/initScrapData.py
    relavent_data = rankingController.addVipList(relavent_data) # same ^ but with gera
    return relavent_data
    # return json_data
####################################################

# IntializeScrape
# WE CAN PROB IGNORE THIS
# THIS IS JUST FOR THST CHECKY "GET FEW BEFORE"
def getChannelFromS3(): # -> return data = getTopChannelsAndSave() = json_data
    # We first get the key/paths from the s3
    sorted_s3_paths =  rankingController.preGetChannelInS3AndTid() # returns a List[str] of S3 Keys/Paths that point to the save s3 channels:
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

# Comes after ?????????
# TODO
# calls yt.addTodoDownlaods(channels)
# calls yt.scrape4VidHref(^)
# calls yt.addTodoDownloads(^)
def initYtdlAudio(channels, isDebug = False):
    # TODO probably need some interface & models for the scrapped-data vs ytdl-data
    chnLimit = 3 if isDebug else 99;
    vidLimit = 3 if isDebug else 10;
    if isDebug:
        scrapped_channels = mocks.initHrefsData.getHrefsData()
        scrapped_channels_with_todos = [{
            "displayname":"LoLGeranimo",
            "url":"lolgeranimo",
            "todos": [
                "/videos/28138895" # cringe vid
                # "/videos/1802413591"
            ],
            "links": [ "/videos/1775892326", "/videos/1752690726", "/videos/1746842079", "/videos/1802413591" ]
        }]
    else:
        scrapped_channels = videoHrefController.scrape4VidHref(channels, True)
        scrapped_channels_with_todos = yt.addTodoDownloads(scrapped_channels)  # scrapped_channels == scrapped_channels_with_todos b/c pass by ref

    


    print ("scrapped_channels_with_todos")
    print ("scrapped_channels_with_todos")
    print ("scrapped_channels_with_todos")
    print (scrapped_channels_with_todos)
    print ()
    print ()
    print ()
    # Download X vids from Y channels
    metadata_Ytdl_list = yt.bigBoyChannelDownloader(scrapped_channels_with_todos, chnLimit=chnLimit, vidDownloadLimit=vidLimit)
    
    #for yt_meta in metadata_Ytdl_list:
        # Nope. Not here
        # yt.transcribefileWhisperAi(yt_meta) # (lolgeranimo, 12341234, {...})

        # print ("Creating caption: " + yt_meta.username + " -> " + yt_meta.link)

        # keybase = S3_CAPTIONS_KEYBASE + yt_meta.username + "/" + CURRENT_DATE_YMD + yt_meta.link.replace("/videos", "") # channels/captions/lolgeranimo/2023-04-18/1747933567
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

    