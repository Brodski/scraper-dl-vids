import controllers.downloadController as downloadController
import controllers.scrapey as scrapey
import mocks.initScrapData
import mocks.initHrefsData
import mocks.ytdlObjMetaDataList
import controllers.yt_download as yt
import datetime
from flask import jsonify, abort



S3_CAPTIONS_KEYBASE = 'channels/captions/'
CURRENT_DATE_YMD = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")



def getTopChannelsAndSave():
    # Make http request to sullygnome 
    topChannels = downloadController.getTopChannels()
    json_data = downloadController.saveTopChannels(topChannels)
    return json_data

def initScrape():
    sorted_s3_paths =  downloadController.getRanking4Scrape()
    combined_channels_list = downloadController.combineAllContent(sorted_s3_paths)
    combined_channels_list = downloadController.addWhiteList(combined_channels_list)
    return combined_channels_list

def initYtdlAudio():
    # TODO probably need some interface & models for the scrapped-data vs ytdl-data
    # href_channel_list = scrapey.scrape4HrefAux()    
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
    metadata_Ytdl_list = yt.downloadChannelsAudio(scrapped_channels_with_todos)
    for yt_meta in metadata_Ytdl_list:
        yt.createCaptionsWhisperAi(yt_meta) # (lolgeranimo, 12341234, {...})
        print ("Creating caption: " + yt_meta.username + " -> " + yt_meta.link)

        # keybase = S3_CAPTIONS_KEYBASE + yt_meta.username + "/" + CURRENT_DATE_YMD + yt_meta.link.replace("/videos", "") # channels/captions/lolgeranimo/2023-04-18/1747933567
        # print ("KEY CAPTIONS=" + keybase)
        # isSuccess = uploadAudioToS3(metadata, keybase) # key = upload 'location' in the s3 bucket 
        # getAlreadyDownloaded

    # each_channels_and_their_ytdl_vids_metadata = mocks.ytdlObjMetaDataList.getYytdlObjMetadataList()
    # updateScrapeHistory(metaData_yt)
    return "done initYtdlAudio"
    return each_channels_and_their_ytdl_vids_metadata
            
    if metaDownloads is None:
        print("failed to download: " + channel['displayname'])
            # abort(400, description="Failed to download: href_channel_list[0]['twitchurl']")
    return metaDownloads

def getAlreadyDownloadedxx():
    return yt.getAlreadyDownloaded()
    