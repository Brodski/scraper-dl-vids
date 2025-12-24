import os
import sys
import time
import traceback
import controllers.MicroDownloader.downloader as downloader
from models.Vod import Vod
from typing import Dict, Iterator, List
# import env_file as env_varz
from env_file import env_varz
from controllers.MicroDownloader.errorEnum import Errorz
import logging
from utils.logging_config import LoggerConfig
from utils.emailer import write_downloader_report
from utils.emailer import sendEmail
from utils.emailer import Status
from utils.ecs_meta import find_aws_logging_info
import utils.generic_stuff as utils_generic


def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()

def printIntro():
    logger.debug("db      =" + env_varz.DATABASE)
    logger.debug("host    =" + env_varz.DATABASE_HOST)
    logger.debug("user    =" + env_varz.DATABASE_USERNAME)
    logger.debug("This instance will download this many: " + env_varz.DWN_BATCH_SIZE)

class MetadataShitty:
    def __init__(self, **kwargs):
        self.vodTitle    = kwargs.get("vodTitle")
        self.vodId       = kwargs.get("vodId")
        self.channelId   = kwargs.get("channelId")
        self.msg         = kwargs.get("msg")
        self.status      = kwargs.get("status")
        self.runtime_ffmpeg_dl   = kwargs.get("runtime_ffmpeg_dl")
        self.runtime_dl          = kwargs.get("runtime_dl")
        self.duration_string     = kwargs.get("duration_string")
        self.vod: Vod            = kwargs.get("vod")

metadata_array_global: List[MetadataShitty] = []

def goDownloadBatch(isDebug=False):
    printIntro()
    cli = find_aws_logging_info()
    start_time = time.time()
    ####################### #
    # LOOP FOR X DOWNLOADS #
    ########################

    logger.debug(f"env_varz.DWN_BATCH_SIZE_OVERRIDE={env_varz.DWN_BATCH_SIZE_OVERRIDE}")
    logger.debug(f"os.getenv(DWN_BATCH_SIZE_OVERRIDE)={os.getenv('DWN_BATCH_SIZE_OVERRIDE')}")
    logger.debug(f"env_varz.DWN_BATCH_SIZE={env_varz.DWN_BATCH_SIZE}")

    download_batch_size = int(env_varz.DWN_BATCH_SIZE)
    # download_batch_size = int(env_varz.DWN_BATCH_SIZE_OVERRIDE) if env_varz.DWN_BATCH_SIZE_OVERRIDE and int(env_varz.DWN_BATCH_SIZE_OVERRIDE) >= 0 else download_batch_size

    vods_list                                  = downloader.getTodoFromDatabase() # "vod" is highest priority 'todo' vod
    magical_ordered_map: Dict[int, List[Vod]]  = utils_generic.convertToFancyMap(vods_list)
    fancy_generator                            = utils_generic.getFromFancyMap(magical_ordered_map)      # <--- smart


    for i in range(download_batch_size):
        logger.debug("===========================================")
        logger.debug(f"    ⚔️ DOWNLOAD BATCH - {i+1} of {download_batch_size}  ")
        logger.debug("===========================================")
        
        #### BOOM ####
        dl_meta = download(fancy_generator, isDebug)

        if dl_meta == Errorz.TOO_BIG or dl_meta == Errorz.DELETED_404 or dl_meta == Errorz.UNAUTHORIZED_403 or dl_meta == None:
            logger.debug("We skipped a download, trying next entry. Error:" + str(dl_meta))
            i += 1
            continue
        logger.debug(f"✅ Finished download {i+1} of {download_batch_size}")
        i += 1

    elapsed_time = time.time() - start_time
    # sendReport(str(int(elapsed_time)))
    write_downloader_report(metadata_array_global, str(int(elapsed_time)))
    return dl_meta

def download(fancy_generator: Iterator[Vod], isDebug=False):
    try:
        ###########################
        # PRE-DOWNLOAD, GET TO-DO #
        ###########################
        vod: Vod        = next(fancy_generator, None)

        ## Post maintenance
        if vod == None or vod.id == None:
            logger.debug("There are zero transcript_status='todo' from the query :O")
            metadata_array_global.append(MetadataShitty(channelId="", vodTitle="", vodId="", status=Status.NOTHING_TODO, msg="Nothing to do apparently"))
            return "nothing to do"

        isSuccess = downloader.lockVodDb(vod, isDebug)
        if not isSuccess:
            logger.debug("No VODS todo!")
            return "No VODS todo!"
        if isSuccess == "race_condition":
            logger.info(f"'Race condition' check found issue on id: {vod.id}. Go again")
            return download(fancy_generator, isDebug)

        logger.debug(f"Going to download: {vod.channels_name_id} - {vod.id}")

        ###################
        # ACTUAL DOWNLOAD #
        ###################
        runtime_ffmpeg_dl = None
        runtime_dl = None
        downloaded_metadata, runtime_dl = downloader.downloadTwtvVidFAST(vod)

        ### ERROR CHECK ###
        if downloaded_metadata in (Errorz.UNAUTHORIZED_403, Errorz.DELETED_404, Errorz.TOO_BIG, Errorz.UNKNOWN ):
            metadata_array_global.append(MetadataShitty(channelId=vod.channels_name_id, vodTitle=vod.title, vodId=vod.id, duration_string=vod.duration_string, status=downloaded_metadata, msg=downloaded_metadata, vod=vod))
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
        
        ####################
        # Post process vod #
        ####################
        downloaded_metadata = downloader.removeNonSerializable(downloaded_metadata)
        outfile, runtime_ffmpeg_dl = downloader.convertVideoToSmallAudio(downloaded_metadata.get('_filename'))
        
        #############
        # Upload DB #
        #############
        s3fileKey = downloader.uploadAudioToS3_v2(downloaded_metadata, outfile, vod)
        if (s3fileKey):
            json_s3_img_keys = downloader.updateImgs_Db(downloaded_metadata, vod)
            vod.title, vod.duration_string = downloader.updateVods_Db(downloaded_metadata, vod, s3fileKey, json_s3_img_keys)
        downloader.cleanUpDownloads(downloaded_metadata)

    #################
    # HANDLE ERRORS #
    #################
    except KeyboardInterrupt:
        logger.debug("\nCtrl+C detected. Exiting gracefully.")
        vod = downloader.unlockVodDb(vod)
        sys.exit()
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}")
        traceback.print_exc()
        tb = traceback.format_exc()  # full stack trace as a string
        metadata_array_global.append(MetadataShitty(channelId=vod.channels_name_id, vodTitle=vod.title, vodId=vod.id, duration_string=vod.duration_string, status=Status.FAILED, msg=tb, runtime_ffmpeg_dl=runtime_ffmpeg_dl, runtime_dl=runtime_dl, vod=vod))
        vod = downloader.unlockVodDb(vod)
        return

    ### SUCCESS ###
    metadata_array_global.append(MetadataShitty(channelId=vod.channels_name_id, vodTitle=vod.title, vodId=vod.id, duration_string=vod.duration_string, vod=vod, status=Status.SUCCESS, runtime_ffmpeg_dl=runtime_ffmpeg_dl, runtime_dl=runtime_dl))
    return downloaded_metadata

