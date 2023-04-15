import controllers.downloadController as downloadController
import controllers.scrapey as scrapey
import mocks.initScrapData
import mocks.initHrefsData
import controllers.yt_download as yt
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

def initScrapeHrefs():
    # href_channel_list = scrapey.scrape4HrefAux()
    href_channel_list = mocks.initHrefsData.getHrefsData()
    print("initScrapeHrefs - href_list:")
    for channel in href_channel_list:
        print(channel)
        # yt.downloadChannelAudio(channel['twitchurl'], channel['links'])
    msg = yt.downloadChannelAudio(href_channel_list[0]['twitchurl'], href_channel_list[0]['links'])
    return msg
        # downloadAudio(h)
        
    # yt.getMeta(href_list[0])
    