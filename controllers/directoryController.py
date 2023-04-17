import controllers.downloadController as downloadController
import controllers.scrapey as scrapey
import mocks.initScrapData
import mocks.initHrefsData
import controllers.yt_download as yt
from flask import jsonify, abort
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
    scrapped_channels_with_todos = yt.addTodoDownloads(scrapped_channels)
    print ("scrapped_channels")
    print ("scrapped_channels")
    print ("scrapped_channels")
    print ("scrapped_channels")
    print ("scrapped_channels")
    print (scrapped_channels)
    print ("todo_downloads_objlist")
    print ("todo_downloads_objlist")
    print ("todo_downloads_objlist")
    print ("todo_downloads_objlist")
    print ("todo_downloads_objlist")
    print (scrapped_channels_with_todos)
    print ()
    print ()
    print ()
    each_channels_and_their_ytdl_vids_metadata = yt.downloadChannelsAudio(scrapped_channels_with_todos)
    # updateScrapeHistory(metaData_yt)
    return each_channels_and_their_ytdl_vids_metadata
            
    if metaDownloads is None:
        print("failed to download: " + channel['displayname'])
            # abort(400, description="Failed to download: href_channel_list[0]['twitchurl']")
    return metaDownloads
            # downloadAudio(h)
    
    # yt.downloadUrl(href_list[0])

def getAlreadyDownloadedxx():
    return yt.getAlreadyDownloaded()
    