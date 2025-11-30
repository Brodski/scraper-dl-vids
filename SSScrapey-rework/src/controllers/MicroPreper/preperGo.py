import math
import time
import traceback
from models.ScrappedChannel import ScrappedChannel
from models.Vod import Vod
from typing import List
import controllers.MicroPreper.databasePreper as databasePreper
import controllers.MicroPreper.seleniumPreper as seleniumPreper
import controllers.MicroPreper.TodoPreper as todoPreper

from env_file import env_varz
import os
import logging
from utils.logging_config import LoggerConfig
from utils.emailer import sendEmail
from models.MetadataP import MetadataP
from utils.ecs_meta import find_aws_logging_info

metadata_p: MetadataP = MetadataP()

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()

def printIntro():
    logger.debug("IT'S RUNNING! WOOOOOOOOOO")
    logger.debug("Will look at these many top channels:")
    logger.debug("  PREP_NUM_CHANNELS:" +  env_varz.PREP_NUM_CHANNELS)
    logger.debug("Will look at this many past broadcasts:")
    logger.debug("  PREP_NUM_VOD_PER_CHANNEL:" +  env_varz.PREP_NUM_VOD_PER_CHANNEL)

def prepare(isDebug=False):
    logger.info("IN PREPER GO")

    printIntro()
    start_time      = time.time()
    logger.info("SLEEPING FOR 2 hours!!!!!!!!")
    logger.info("SLEEPING FOR 2 hours!!!!!!!!")
    logger.info("SLEEPING FOR 2 hours!!!!!!!!")
    logger.info("SLEEPING FOR 2 hours!!!!!!!!")
    logger.info("SLEEPING FOR 2 hours!!!!!!!!")
    logger.info("SLEEPING FOR 2 hours!!!!!!!!")
    logger.info("SLEEPING FOR 2 hours!!!!!!!!")
    logger.info("SLEEPING FOR 2 hours!!!!!!!!")
    logger.info("SLEEPING FOR 2 hours!!!!!!!!")
    logger.info("SLEEPING FOR 2 hours!!!!!!!!")
    find_aws_logging_info()
    time.sleep(100)
    # Make http request to sullygnome. 3rd party website
    topChannels = todoPreper.getTopChannelsSully() 
    topChannels = todoPreper.addVipList(topChannels, isDebug) # same ^ but with gera

    # Convert json respone to objects
    scrapped_channels: List[ScrappedChannel] = todoPreper.instantiateJsonToClassObj(topChannels) # relevant_data = /mocks/initScrapData.py

    # Via selenium & browser. Find videos's url, get anchor tags href
    scrapped_channels: List[ScrappedChannel] = seleniumPreper.scrape4VidHref(scrapped_channels, isDebug) # returns -> /mocks/initHrefsData.py

    updateShit(scrapped_channels)
    elapsed_time = math.ceil(time.time() - start_time)
    elapsed_time_MIN = round(elapsed_time / 60, 2)
    logger.info("++++++++++++++++++++++++++++")
    logger.info("++++++++++++++++++++++++++++")
    logger.info("++++++++++++++++++++++++++++")
    logger.info("FINISHED! TOTAL TIME RUNNING = " + str(elapsed_time) + f" = {str(elapsed_time_MIN)} minutes")
    logger.info("FINISHED! TOTAL TIME RUNNING = " + str(elapsed_time) + f" = {str(elapsed_time_MIN)} minutes")
    logger.info("FINISHED! TOTAL TIME RUNNING = " + str(elapsed_time) + f" = {str(elapsed_time_MIN)} minutes")
    logger.info("DONE!")
    metadata_p.elapsed_time = elapsed_time
    metadata_p.format_and_email_msg()


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
        all_channels_minus_scrapped: List[ScrappedChannel] = doWithCallback(lambda: databasePreper.getNewOldChannelsFromDB(scrapped_channels), 0)
        doWithCallback(lambda: databasePreper.updateChannelDataByHtmlIteratively(all_channels_minus_scrapped + scrapped_channels), 0) # This gaurentees there will be no overlap.
        doWithCallback(lambda: databasePreper.updateChannelRankingLazily(scrapped_channels), 0)
        doWithCallback(lambda: databasePreper.updateVodsDb(scrapped_channels), 0)
        doWithCallback(lambda: databasePreper.updateChannelWatchStats(all_channels_minus_scrapped + scrapped_channels), 0)
        doWithCallback(lambda: databasePreper.deleteOldTodos(), 0)
    except Exception as e:
        logger.error(f"An error occurred in updateShit: {str(e)}")
        the_msg = "An error occurred in updateShit:\n" + ''.join(traceback.format_stack())

        subject = f"Preper {os.getenv('ENV')} - (error)"
        sendEmail(subject, the_msg)

    logger.info("Finished step 1 Preper-Service")
    return "Finished step 1 Preper-Service"
