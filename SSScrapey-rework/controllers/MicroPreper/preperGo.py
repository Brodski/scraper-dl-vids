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
    
    # Convert json respone to objects
    scrapped_channels: List[ScrappedChannel] = todoPreper.instantiateJsonToClassObj(topChannels) # relevant_data = /mocks/initScrapData.py
    scrapped_channels: List[ScrappedChannel] = todoPreper.addVipList(scrapped_channels, isDebug) # same ^ but with gera

    # Via selenium & browser. Find videos's url, get anchor tags href
    scrapped_channels: List[ScrappedChannel] = seleniumPreper.scrape4VidHref(scrapped_channels, isDebug) # returns -> /mocks/initHrefsData.py

    # Done
    try:
        databasePreper.addNewChannelToDb(scrapped_channels)
        databasePreper.addRankingsForTodayDb(scrapped_channels) # Optional??
        databasePreper.updateChannelRankingLazily(scrapped_channels)
        databasePreper.updateVodsDb(scrapped_channels)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    print("Finished step 1 Preper-Service")
    return "Finished step 1 Preper-Service"