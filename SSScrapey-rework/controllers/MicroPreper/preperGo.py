import traceback
from models.ScrappedChannel import ScrappedChannel
from models.Vod import Vod
from typing import List
import controllers.MicroPreper.databasePreper as databasePreper
import controllers.MicroPreper.seleniumPreper as seleniumPreper
import controllers.MicroPreper.TodoPreper as todoPreper
import datetime
import env_file as env_varz
import json
import os

def prepare(isDebug=False):
    print ("IT'S RUNNING! WOOOOOOOOOO")
    # Make http request to sullygnome. 3rd party website
    topChannels = todoPreper.getTopChannels() 
    topChannels = todoPreper.addVipList(topChannels, isDebug) # same ^ but with gera
    # Convert json respone to objects
    scrapped_channels: List[ScrappedChannel] = todoPreper.instantiateJsonToClassObj(topChannels) # relevant_data = /mocks/initScrapData.py

    # Via selenium & browser. Find videos's url, get anchor tags href
    scrapped_channels: List[ScrappedChannel] = seleniumPreper.scrape4VidHref(scrapped_channels, isDebug) # returns -> /mocks/initHrefsData.py

    try:
        databasePreper.addNewChannelToDb(scrapped_channels)
        all_channels_minus_scrapped_plus_vip: List[ScrappedChannel] = databasePreper.getNewOldChannelsFromDB(scrapped_channels)
        databasePreper.updateChannelDataByHtmlIteratively(all_channels_minus_scrapped_plus_vip)
        databasePreper.addRankingsForTodayDb(scrapped_channels) # Optional??
        databasePreper.updateChannelRankingLazily(scrapped_channels)
        databasePreper.updateChannelWatchStats(scrapped_channels + all_channels_minus_scrapped_plus_vip)
        databasePreper.updateVodsDb(scrapped_channels)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(traceback.format_exc())
    print("Finished step 1 Preper-Service")
    return "Finished step 1 Preper-Service"