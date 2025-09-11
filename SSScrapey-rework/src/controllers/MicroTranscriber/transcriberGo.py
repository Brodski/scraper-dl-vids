# import controllers.MicroTranscriber.cloudwatch as cloudwatch
import math
import sys
from controllers.MicroTranscriber.cloudwatch import Cloudwatch 
from controllers.MicroTranscriber.audio2Text_faster_whisper import Audio2Text 
from models.Vod import Vod
from typing import Dict, List
import boto3
import controllers.MicroTranscriber.transcriber as transcriber
import controllers.MicroTranscriber.split_ffmpeg as split_ffmpeg
import datetime
import env_file as env_varz
import json
import os
import time
import traceback
import urllib.parse
import urllib.request
from typing import List
import logging
from utils.logging_config import LoggerConfig
from models.Splitted import Splitted
from datetime import datetime

# logger = Cloudwatch.log
def logger():
    pass
logger: logging.Logger = LoggerConfig("micro", env_varz.WHSP_IS_CLOUDWATCH == "True").get_logger()

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def printIntro():
    logger.info("Current vast.ai container_id:")
    logger.info('   CONTAINER_ID! ' + str(os.getenv("CONTAINER_ID")))
    logger.info("Currently running this nth instance:" + env_varz.TRANSCRIBER_INSTANCE_CNT)
    logger.info(f"   TRANSCRIBER_INSTANCE_CNT: {env_varz.TRANSCRIBER_INSTANCE_CNT}")
    logger.info("Total num instances")
    logger.info(f"   TRANSCRIBER_NUM_INSTANCES: {env_varz.TRANSCRIBER_NUM_INSTANCES}")
    logger.info("VODs transcribed per instance:")
    logger.info(f"   TRANSCRIBER_VODS_PER_INSTANCE: {env_varz.TRANSCRIBER_VODS_PER_INSTANCE}")

def goTranscribeBatch(isDebug=False, args=None, mofo: List[Splitted] | None = None):
    printIntro()
    if args:
        if args.query_todo:
            vods_list: List[Vod] = transcriber.getTodoFromDb()
            pretty_print_query_vods(vods_list)
            return
        if args.num_vods_override:
            env_varz.NUM_CHANNELS = args.num_vods_override

    print("ENDNNDNDNDNDN")

    start_time = time.time()
    download_batch_size = 1 if env_varz.TRANSCRIBER_VODS_PER_INSTANCE is None else env_varz.TRANSCRIBER_VODS_PER_INSTANCE
    completed_vods_list: List[Vod] = []
    failed_vods_list: List[Vod] = []
    logger.debug("Transcriber start!")
    logger.debug(f"TRANSCRIBE BATCH SIZE: {download_batch_size}")
    download_batch_size = 2
    for i in range(0, download_batch_size):
        print("===========================================")
        print(f"    TRANSCRIBE BATCH - {i+1} of {download_batch_size}  ")
        print("===========================================")

        Audio2Text.download_batch_size = download_batch_size
        Audio2Text.current_num = i + 1

        result: Dict[Vod, bool] = transcribe(isDebug, mofo)
        vod: Vod = result["vod"]

        logger.info(f"   (goTranscribeBatch) Finished Index {i}")
        logger.info(f"   (goTranscribeBatch) download_batch_size: {download_batch_size}")
        if result["isPass"]:
            completed_vods_list.append(vod)
        else:
            failed_vods_list.append(vod)
    logger.info("---------------------------------------------")
    logger.info("---------------------------------------------")
    logger.info("---------------------------------------------")
    elapsed_time = math.ceil(time.time() - start_time)
    logger.info("FINISHED! TOTAL TIME RUNNING= " + str(elapsed_time))
    logger.info("FINISHED! TOTAL TIME RUNNING= " + str(elapsed_time))
    logger.info("FINISHED! TOTAL TIME RUNNING= " + str(elapsed_time))
    logger.info("Completed: ")
    for v in failed_vods_list:
        logger.info(f"FAILED: {v.channels_name_id} - {v.title} - id: {v.id}")
    for v in completed_vods_list:
        logger.info(f"COMPLETE: {v.channels_name_id} - {v.title} - id: {v.id}")
        # logger.info(f"Audio uploaded to: {env_varz.BUCKET_DOMAIN}/{s3CapFileKey}")
    for t in Audio2Text.completed_uploaded_tscripts:
        try:
            if t.endswith(".json"):
                logger.debug(f"Transcripts @ {t}")
                logger.debug(f"")
        except:
            logger.error("oops, .endswith() is not a real method")

    # time.sleep(100) 
    logger.debug("gg ending")
    logger.debug("gg ending")
    return "gg ending"

def transcribe(isDebug=False, mofo: List[Splitted] | None = None) -> Dict[Vod, bool]:
    # Setup. Get Vod
    start_time = time.time()
    vods_list = transcriber.getTodoFromDb()
    vod: Vod = vods_list[0] if len(vods_list) > 0 else None
    relative_path = None
    logger.debug('IN THEORY, AUDIO TO TEXT THIS:')
    if not vod and not isDebug:
        logger.info("jk, vod is null, nothing to do. no audio2text_need")
        return None
    if isDebug:
        vod = getDebugVod(vod)
    logger.debug(vod.print())

    transcriber.setSemaphoreDb(vod) # Set TranscrptStatus = "transcribing"

    # Do the transcribing
    try:
        relative_path: str = transcriber.downloadAudio(vod)
        print("env_varz.WHSP_IS_BIG_FILES_ENABLED: " + str(env_varz.WHSP_IS_BIG_FILES_ENABLED))

        if env_varz.WHSP_IS_BIG_FILES_ENABLED == "True":
            print("YES YEYSYSEYYEYSY  BIG_FILES_ENABLED")
            splitted_list: List[Splitted] = split_ffmpeg.splitHugeFile(vod, relative_path)
        elif mofo == None:
            split = Splitted(relative_path = relative_path)
            splitted_list = [split]
        else: 
            splitted_list = mofo
        saved_caption_files = Audio2Text.doWhisperStuff(vod, splitted_list)
        # saved_caption_files = transcriber.doInsaneWhisperStuff(vod, relative_path, isDebug)

        transcripts_s3_key_arr = transcriber.uploadCaptionsToS3(saved_caption_files, vod)
        transcriber.setCompletedStatusDb(transcripts_s3_key_arr, vod)
        transcriber.deleteAudioS3(vod)
    except KeyboardInterrupt:
        logger.debug("\nCtrl+C detected. Exiting gracefully.")
        transcriber.unsetSemaphoreDb(vod) # "vod" is highest priority 'todo' vod
        sys.exit()
    except Exception as e:
        error_message = f"ERROR Transcribing vod: {e}"
        stack_trace = traceback.format_exc()
        logger.error(error_message + "\n" + stack_trace)
        transcriber.unsetSemaphoreDb(vod)
        return {"vod": vod, "isPass": False}

    transcriber.cleanUpFiles(relative_path)
    logger.debug("Finished step 3 Transcriber-Service")
    logger.info(f"Time taken for {vod.channels_name_id}-{vod.id}: { math.ceil(time.time() - start_time)}")
    return {"vod": vod, "isPass": True}

def getDebugVod(vod: Vod):
    # tuple =  ('2143646862', 'kaicenat', '⚔️100+ HR STREAM⚔️ELDEN RING⚔️CLICK HERE⚔️GAMER⚔️BIGGEST DWARF⚔️ELITE⚔️PRAY 4 ME⚔️', '78', '1:18', 39744, 'https://www.twitch.tv/videos/40792901', datetime.datetime(2013, 8, 2, 18, 26, 30), 'audio2text_need', 1, 'https://static-cdn.jtvnw.net/jtv_user_pictures/1d8cd548-04fa-49fb-bfcd-f222f73482b6-profile_image-70x70.png', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/kaicenat/2143646862/100%252B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.opus', '-1', 'English')
    tuple =  ('40792901', 'nmplol', 'And you will know my name is the LORD', '78', '1:18', 39744, 'https://www.twitch.tv/videos/40792901', datetime.datetime(2013, 8, 2, 18, 26, 30), 'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/511e8d0d2a/nmplol_6356312704_6356312704/thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/nmplol/40792901/And_you_will_know_my_name_is_the_LORD-v40792901.opus', '-1', 'English')
    # tuple =  ('1964894986', 'jd_onlymusic', '夜市特攻隊「永和樂華夜市」ft. 陳老師', '732', '12:12', 1205, 'https://www.twitch.tv/videos/1964894986',datetime.datetime(2023, 10, 2, 18, 26, 30),'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d3vd9lfkzbru3h/e8c73b0847f78c0231fc_jd_onlymusic_40759279447_1698755215//thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/jd_onlymusic/1964894986/ft.-v1964894986.opus','-3', 'Chinese')
    # tuple =  ('28138895', 'geranimo', 'The Geraniproject! I Love You Guys!!!', '1047', '17:26', 786, 'https://www.twitch.tv/videos/28138895',datetime.datetime(2023, 10, 2, 18, 26, 30),'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d3vd9lfkzbru3h/e8c73b0847f78c0231fc_jd_onlymusic_40759279447_1698755215//thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/geranimo/28138895/The_Geraniproject_I_Love_You_Guys-v28138895.opus','-2', 'English')
    Id, ChannelNameId, Title, Duration, DurationString,ViewCount,WebpageUrl,StreamDate, TranscriptStatus, Priority, Thumbnail,TodoDate,S3Audio,ChanCurrentRank,Language  = tuple
    vod = Vod(id=Id, title=Title, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, todo_date=TodoDate, stream_date=StreamDate, s3_audio=S3Audio, language=Language)
    return vod





def truncate(text, max_len):
    return text if len(text) <= max_len else text[:max_len - 1] + "…"

def pretty_print_query_vods(vods_list):
    import shutil

    # Fixed/default width
    col_channel = 15
    col_id = 10
    col_status = 12

    term_width = shutil.get_terminal_size((120, 20)).columns 
    col_title = term_width - (col_channel + col_id + col_status + 13)  # 9 = padding & separators (3 x Columns)
    
    # Header
    print(f"{'Channel':<{col_channel}} | {'VOD ID':<{col_id}} | {'Title':<{col_title}} | {'Status':<{col_status}}")
    print("-" * term_width)

    for vod in vods_list:
        ch = truncate(vod.channels_name_id, col_channel)
        vid = truncate(str(vod.id), col_id)
        title = truncate(vod.title, col_title)
        status = truncate(vod.transcript_status, col_status)

        print(f"{ch:<{col_channel}} | {vid:<{col_id}} | {title:<{col_title}} | {status:<{col_status}}")
