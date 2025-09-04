import traceback
from models.ScrappedChannel import ScrappedChannel
from models.Vod import Vod
from typing import List
import controllers.MicroPreper.databasePreper as databasePreper
import controllers.MicroPreper.seleniumPreper as seleniumPreper
import controllers.MicroPreper.TodoPreper as todoPreper
import env_file as env_varz
import os
import logging
from utils.logging_config import LoggerConfig

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()

def printIntro():
    logger.debug("IT'S RUNNING! WOOOOOOOOOO")
    logger.debug("Will look at these many top channels:")
    logger.debug("  NUM_CHANNELS:" +  env_varz.NUM_CHANNELS)
    logger.debug("Will look at this many past broadcasts:")
    logger.debug("  NUM_VOD_PER_CHANNEL:" +  env_varz.NUM_VOD_PER_CHANNEL)

def prepare(isDebug=False):
    printIntro()
    
    # Make http request to sullygnome. 3rd party website
    topChannels = todoPreper.getTopChannelsSully() 
    topChannels = todoPreper.addVipList(topChannels, isDebug) # same ^ but with gera

    # Convert json respone to objects
    scrapped_channels: List[ScrappedChannel] = todoPreper.instantiateJsonToClassObj(topChannels) # relevant_data = /mocks/initScrapData.py

    # Via selenium & browser. Find videos's url, get anchor tags href
    scrapped_channels: List[ScrappedChannel] = seleniumPreper.scrape4VidHref(scrapped_channels, isDebug) # returns -> /mocks/initHrefsData.py

    updateShit(scrapped_channels)

def doWithCallback(callback, counter):
    if counter > 3:
        logger.error("Counter > 3. Ending. Shit is broke")
        return None
    try:
        return callback()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())
        return doWithCallback(callback, counter + 1)

def updateShit(scrapped_channels: List[ScrappedChannel]):
    try:
        doWithCallback(lambda: databasePreper.addNewChannelToDb(scrapped_channels), 0)
        logger.debug("wtf is happening here")
        all_channels_minus_scrapped: List[ScrappedChannel] = doWithCallback(lambda: databasePreper.getNewOldChannelsFromDB(scrapped_channels), 0)
        doWithCallback(lambda: databasePreper.updateChannelDataByHtmlIteratively(all_channels_minus_scrapped + scrapped_channels), 0) # This gaurentees there will be no overlap.
        doWithCallback(lambda: databasePreper.updateChannelRankingLazily(scrapped_channels), 0)
        doWithCallback(lambda: databasePreper.updateVodsDb(scrapped_channels), 0)
        doWithCallback(lambda: databasePreper.updateChannelWatchStats(all_channels_minus_scrapped + scrapped_channels), 0)
        doWithCallback(lambda: databasePreper.deleteOldTodos(), 0)
    except Exception as e:
        logger.error(f"An error occurred in updateShit: {str(e)}")
    logger.info("Finished step 1 Preper-Service")
    return "Finished step 1 Preper-Service"
