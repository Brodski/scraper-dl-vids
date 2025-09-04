import sys
import controllers.MicroDownloader.downloader as downloader
from models.Vod import Vod
from typing import List
import env_file as env_varz
from controllers.MicroDownloader.errorEnum import Errorz
import logging
from utils.logging_config import LoggerConfig

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()

def printIntro():
    logger.debug("db      =" + env_varz.DATABASE)
    logger.debug("host    =" + env_varz.DATABASE_HOST)
    logger.debug("user    =" + env_varz.DATABASE_USERNAME)
    logger.debug("Will download this many: " + env_varz.NUM_VOD_PER_CHANNEL)
    logger.debug("There is only 1 ecs instance for Downloader. Nothing crazy")
    # Note: NUM_VOD_PER_CHANNEL doesnt have much effect. Looks at X recent vods from the database (todo, completed, audio2text_need, ect) then gets the "todo" one
    #       It is so that we dont over prioritize all the vods from the 'top streamers'

def goDownloadBatch(isDebug=False, args={}):
    printIntro()

    if args.quick_dl:
        env_varz.DWN_IS_SHORT_DEV_DL = args.quick_dl

    # download_batch_size = int(env_varz.DWN_BATCH_SIZE)
    download_batch_size = int(env_varz.NUM_CHANNELS) 
    i = 0
    gaurdrail = 25
    while i < download_batch_size and i < gaurdrail:
        gaurdrail -= 1
        logger.debug("===========================================")
        logger.debug(f"    DOWNLOAD BATCH - {i+1} of {download_batch_size}  ")
        logger.debug("===========================================")
        dl_meta = download(i, isDebug)
        if dl_meta == Errorz.TOO_BIG or dl_meta == Errorz.DELETED_404 or dl_meta == Errorz.UNAUTHORIZED_403:
            logger.debug("We skipped a download, trying next entry. Error:" + str(dl_meta))
            continue
        logger.debug(f"Finished download # {i+1} of {download_batch_size}")
        i += 1
    return dl_meta

def download(i, isDebug=False):
    vod = downloader.getTodoFromDatabase(i, isDebug=isDebug) # "vod" is highest priority 'todo' vod
    if vod == None:
        logger.debug("There are zero transcript_status='todo' from the query :O")
        return "nothing to do"
    # Download vod from twitch
    vod.printDebug()
    isSuccess = downloader.lockVodDb(vod, isDebug)
    # isSuccess = True
    if not isSuccess:
        logger.debug("No VODS todo!")
        return "No VODS todo!"

    logger.debug(f"Going to download: {vod.channels_name_id} - {vod.id} - title: {vod.title}")

    try:
        downloaded_metadata = downloader.downloadTwtvVidFAST(vod, isDebug)
    except KeyboardInterrupt:
        logger.debug("\nCtrl+C detected. Exiting gracefully.")
        vod = downloader.unlockVodDb(vod) # "vod" is highest priority 'todo' vod
        sys.exit()        

    if downloaded_metadata == Errorz.UNAUTHORIZED_403:
        downloader.updateErrorVod(vod,"unauthorized")
        logger.debug("nope gg. 403 sub only")
        return Errorz.UNAUTHORIZED_403
    if downloaded_metadata == Errorz.DELETED_404:
        downloader.updateErrorVod(vod, "deleted")
        logger.debug("nope gg. 404 delete")
        return Errorz.DELETED_404
    if downloaded_metadata == Errorz.TOO_BIG:
        downloader.updateErrorVod(vod, "too_big")
        logger.debug("nope gg. too big")
        return Errorz.TOO_BIG
    if downloaded_metadata == None or downloaded_metadata == Errorz.UNKNOWN:
        downloader.updateErrorVod(vod, "unknown")
        logger.debug("nope gg. Some other error")
        return Errorz.UNKNOWN

    # Post process vod
    downloaded_metadata = downloader.removeNonSerializable(downloaded_metadata)
    downloaded_metadata, outfile = downloader.convertVideoToSmallAudio(downloaded_metadata)
    # Upload DB
    s3fileKey = downloader.uploadAudioToS3_v2(downloaded_metadata, outfile, vod)
    if (s3fileKey):
        json_s3_img_keys = downloader.updateImgs_Db(downloaded_metadata, vod)
        downloader.updateVods_Db(downloaded_metadata, vod.id, s3fileKey, json_s3_img_keys)
    downloader.cleanUpDownloads(downloaded_metadata)

    return downloaded_metadata