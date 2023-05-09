import controllers.rankingController as rankingController
import controllers.rankingController as rankingController
import mocks.initScrapData
import mocks.initHrefsData
import mocks.ytdlObjMetaDataList
import controllers.yt_download as yt
import datetime
# from flask import jsonify, abort



S3_CAPTIONS_KEYBASE = 'channels/captions/'
CURRENT_DATE_YMD = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")



def getTopChannelsAndSave():
    # Make http request to sullygnome. 3rd party website
    topChannels = rankingController.getTopChannels(numChannels=30) 
    # Saves those channels to S3 
    json_data = rankingController.saveTopChannels(topChannels)
    return json_data

def initScrape():
    sorted_s3_paths =  rankingController.getRanking4Scrape()
    combined_channels_list = rankingController.combineAllContent(sorted_s3_paths)
    combined_channels_list = rankingController.addVipList(combined_channels_list)
    # Returns: 
        #     {
        #     "displayname": "LoLGeranimo",
        #     "language": "English",
        #     "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
        #     "twitchurl": "https://www.twitch.tv/lolgeranimo",
        #     "url": "lolgeranimo"
        #   },...,
    return combined_channels_list

def initYtdlAudio():
    # TODO probably need some interface & models for the scrapped-data vs ytdl-data
    # href_channel_list = rankingController.scrape4H30efAux()    
    scrapped_channels = mocks.initHrefsData.getHrefsData()
    scrapped_channels_with_todos = yt.addTodoDownloads(scrapped_channels)  # scrapped_channels == scrapped_channels_with_todos b/c pass by ref
    isDebugTime = True
    if (isDebugTime == True ):
        scrapped_channels_with_todos = [{
            "displayname":"LoLGeranimo",
            "url":"lolgeranimo",
            "todos": [
                "/videos/28138895" # cringe vid
                # "/videos/1802413591"
            ],
            "links": [ "/videos/1775892326", "/videos/1752690726", "/videos/1746842079", "/videos/1802413591" ]
        }]
    print ("todo_downloads_objlist")
    print ("todo_downloads_objlist")
    print ("todo_downloads_objlist")
    print (scrapped_channels_with_todos)
    print ()
    print ()
    print ()
    # Download X vids from Y channels
    metadata_Ytdl_list = yt.bigBoyChannelDownloader(scrapped_channels_with_todos, chnLimit=3, vidDownloadLimit=3)
    #for yt_meta in metadata_Ytdl_list:
        # Nope. Not here
        # yt.transcribefileWhisperAi(yt_meta) # (lolgeranimo, 12341234, {...})

        # print ("Creating caption: " + yt_meta.username + " -> " + yt_meta.link)

        # keybase = S3_CAPTIONS_KEYBASE + yt_meta.username + "/" + CURRENT_DATE_YMD + yt_meta.link.replace("/videos", "") # channels/captions/lolgeranimo/2023-04-18/1747933567
        # print ("KEY CAPTIONS=" + keybase)
        # isSuccess = uploadAudioToS3(metadata, keybase) # key = upload 'location' in the s3 bucket 
        # getAlreadyDownloaded

    # each_channels_and_their_ytdl_vids_metadata = mocks.ytdlObjMetaDataList.getYytdlObjMetadataList()
    # updateScrapeHistory(metaData_yt)
    return "done initYtdlAudio"
    return metadata_Ytdl_list
            
    if metaDownloads is None:
        print("failed to download: " + channel['displayname'])
            # abort(400, description="Failed to download: href_channel_list[0]['twitchurl']")
    return metaDownloads

def getAlreadyDownloadedxx():
    return yt.getAlreadyDownloaded()
    