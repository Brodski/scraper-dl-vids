import traceback
from models.ScrappedChannel import ScrappedChannel
from models.Vod import Vod
from typing import List
import controllers.MicroPreper.databasePreper as databasePreper
import controllers.MicroPreper.seleniumPreper as seleniumPreper
import controllers.MicroPreper.TodoPreper as todoPreper
import env_file as env_varz
import os

def printIntro():
    print("IT'S RUNNING! WOOOOOOOOOO")
    print("Will look at these many top channels:")
    print("  PREP_SELENIUM_NUM_CHANNELS:", env_varz.PREP_SELENIUM_NUM_CHANNELS)
    print("Will look at this many past broadcasts:")
    print("  PREP_SELENIUM_NUM_VODS_PER:", env_varz.PREP_SELENIUM_NUM_VODS_PER)

def prepare(isDebug=False):
    printIntro()
    # Make http request to sullygnome. 3rd party website
    topChannels = todoPreper.getTopChannelsSully() 
    topChannels = todoPreper.addVipList(topChannels, isDebug) # same ^ but with gera
    # Convert json respone to objects
    scrapped_channels: List[ScrappedChannel] = todoPreper.instantiateJsonToClassObj(topChannels) # relevant_data = /mocks/initScrapData.py

    # Via selenium & browser. Find videos's url, get anchor tags href
    scrapped_channels: List[ScrappedChannel] = seleniumPreper.scrape4VidHref(scrapped_channels, isDebug) # returns -> /mocks/initHrefsData.py

    try:
        databasePreper.addNewChannelToDb(scrapped_channels)
        all_channels_minus_scrapped: List[ScrappedChannel] = databasePreper.getNewOldChannelsFromDB(scrapped_channels)
        databasePreper.updateChannelDataByHtmlIteratively(all_channels_minus_scrapped + scrapped_channels) # This gaurentees there will be no overlap.
        # databasePreper.addRankingsForTodayDb(scrapped_channels) # Optional
        databasePreper.updateChannelRankingLazily(scrapped_channels)
        databasePreper.updateVodsDb(scrapped_channels)
        databasePreper.updateChannelWatchStats(all_channels_minus_scrapped + scrapped_channels)

        databasePreper.deleteOldTodos()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(traceback.format_exc())
    print("Finished step 1 Preper-Service")
    return "Finished step 1 Preper-Service"