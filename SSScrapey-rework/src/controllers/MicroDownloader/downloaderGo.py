import sys
import time
import traceback
import controllers.MicroDownloader.downloader as downloader
from models.Vod import Vod
from typing import Dict, List
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
        self.runtime_ffmpeg_dl      = kwargs.get("runtime_ffmpeg_dl")
        self.runtime_dl          = kwargs.get("runtime_dl")
        self.duration_string     = kwargs.get("duration_string")

metadata_array_global: List[MetadataShitty] = []

def goDownloadBatch(isDebug=False):
    printIntro()
    cli = find_aws_logging_info()
    start_time = time.time()
    ####################### #
    # LOOP FOR X DOWNLOADS #
    ########################

    download_batch_size = int(env_varz.DWN_BATCH_SIZE)

    i = 0
    gaurdrail = 15
    while i < download_batch_size and i < gaurdrail:
        gaurdrail -= 1
        logger.debug("===========================================")
        logger.debug(f"    ⚔️ DOWNLOAD BATCH - {i+1} of {download_batch_size}  ")
        logger.debug("===========================================")
        dl_meta = download(i, isDebug)
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

def download(i, isDebug=False):
    try:
        ###########################
        # PRE-DOWNLOAD, GET TO-DO #
        ###########################

        # vod = downloader.getTodoFromDatabase(i, isDebug=isDebug) # "vod" is highest priority 'todo' vod
        vods_list       = downloader.getTodoFromDatabase(i, isDebug=isDebug) # "vod" is highest priority 'todo' vod
        magical_ordered_map: Dict[int, List[Vod]]  = utils_generic.convertToFancyMap(vods_list)
        gen             = utils_generic.getFromFancyMap(magical_ordered_map)      # <--- smart
        vod: Vod        = next(gen, None)

        ## Post maintenance
        if vod == None or vod.id == None:
            logger.debug("There are zero transcript_status='todo' from the query :O")
            metadata_array_global.append(MetadataShitty(channelId="", vodTitle="", vodId="", status=Status.NOTHING_TODO, msg="Nothing to do apparently"))
            return "nothing to do"

        isSuccess = downloader.lockVodDb(vod, isDebug)
        if not isSuccess:
            logger.debug("No VODS todo!")
            return "No VODS todo!"

        logger.debug(f"Going to download: {vod.channels_name_id} - {vod.id}")

        ###################
        # ACTUAL DOWNLOAD #
        ###################
        runtime_ffmpeg_dl = None
        runtime_dl = None
        downloaded_metadata, runtime_dl = downloader.downloadTwtvVidFAST(vod)

        ### ERROR CHECK ###
        if downloaded_metadata in (Errorz.UNAUTHORIZED_403, Errorz.DELETED_404, Errorz.TOO_BIG, Errorz.UNKNOWN ):
            metadata_array_global.append(MetadataShitty(channelId=vod.channels_name_id, vodTitle=vod.title, vodId=vod.id, duration_string=vod.duration_string, status=downloaded_metadata, msg=downloaded_metadata))
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
        downloaded_metadata, outfile, runtime_ffmpeg_dl = downloader.convertVideoToSmallAudio(downloaded_metadata)
        
        #############
        # Upload DB #
        #############
        s3fileKey = downloader.uploadAudioToS3_v2(downloaded_metadata, outfile, vod)
        if (s3fileKey):
            json_s3_img_keys = downloader.updateImgs_Db(downloaded_metadata, vod)
            vod.title, vod.duration_string = downloader.updateVods_Db(downloaded_metadata, vod.id, s3fileKey, json_s3_img_keys)
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
        metadata_array_global.append(MetadataShitty(channelId=vod.channels_name_id, vodTitle=vod.title, vodId=vod.id, duration_string=vod.duration_string, status=Status.FAILED, msg=tb, runtime_ffmpeg_dl=runtime_ffmpeg_dl, runtime_dl=runtime_dl))
        vod = downloader.unlockVodDb(vod)
        return

    ### SUCCESS ###
    metadata_array_global.append(MetadataShitty(channelId=vod.channels_name_id, vodTitle=vod.title, vodId=vod.id, duration_string=vod.duration_string, status=Status.SUCCESS, runtime_ffmpeg_dl=runtime_ffmpeg_dl, runtime_dl=runtime_dl))
    return downloaded_metadata


##############
# SEND EMAIL #
# i vibe coded this
##############
# from collections import Counter
# def sendReport(elapsed_time=0):
#     total = env_varz.DWN_BATCH_SIZE
#     status_counter = Counter()

#     msg_lines = []
#     seconds = int(elapsed_time)
#     mins    = seconds / 60
#     hours   = mins / 60
#     msg_lines.append(f"TOTAL TIME: {seconds:.2f} secs = {mins:.2f} min = {hours:.2f} hours")
#     msg_lines.append("\n")
#     for idx, metadata in enumerate(metadata_array_global):
#         status = getattr(metadata, 'status', 'N/A')
#         status_counter[status] += 1

#         message         = getattr(metadata, 'msg', '')
#         channel         = getattr(metadata, 'channelId', 'Unknown')
#         vod_id          = getattr(metadata, 'vodId', 'Unknown')
#         vod_title       = getattr(metadata, 'vodTitle', 'Untitled')
#         duration_string = getattr(metadata, 'duration_string', 'NA')
#         runtime_ffmpeg_dl  = metadata.runtime_ffmpeg_dl or -69
#         runtime_dl      = metadata.runtime_dl or -69
        
#         runtime_ffmpeg_dl if runtime_ffmpeg_dl else 0
#         runtime_dl if runtime_dl else 0

#         msg_lines.append(
#             f"-------------{idx}--------------\n"
#             f"Status: {status}\n"
#             f"Channel ID: {channel}\n"
#             f"VOD Title: {vod_title}\n"
#             f"VOD ID: {vod_id}\n"
#             f"Duration: {duration_string}\n"
#             f"runtime_ffmpeg_dl (sec): {float(runtime_ffmpeg_dl):.2f}\n"
#             f"runtime_dl (sec): {float(runtime_dl):.2f}\n"
#             f"Message: {message}\n"
#         )

#     # Build summary
#     summary_lines = ["Download Report Summary:", f"Total expected items: {total}", f"Total actual item {str(len(metadata_array_global))}"]
#     for status, count in status_counter.items():
#         summary_lines.append(f"{status}: {count}")

#     # Combine summary and detailed report
#     cli = find_aws_logging_info()
#     report_message = "\n".join(summary_lines + [""] + msg_lines)
#     report_message + "\n" + cli

#     sendEmail(f"Downloader {env_varz.ENV} report", report_message)
#     logger.info(report_message)
#     # logger.debug(f"Going to download: {vod.channels_name_id} - {vod.id} - title: {vod.title}")