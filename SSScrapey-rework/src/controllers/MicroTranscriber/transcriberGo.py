# import controllers.MicroTranscriber.cloudwatch as cloudwatch
from controllers.MicroTranscriber.cloudwatch import Cloudwatch 
from controllers.MicroTranscriber.audio2Text_faster_whisper import Audio2Text 
from models.Vod import Vod
from typing import Dict, List
import boto3
import controllers.MicroTranscriber.transcriber as transcriber
import datetime
import env_file as env_varz
import json
import os
import time
import traceback
import urllib.parse
import urllib.request
from typing import List

def logger():
    pass
logger = Cloudwatch.log


def goTranscribeBatch(isDebug=False):
    start_time = time.time()
    download_batch_size = int(env_varz.WHSP_BATCH_SIZE)
    completed_vods_list: List[Vod] = []
    failed_vods_list: List[Vod] = []
    logger("Transcriber start! ")
    logger('CONTAINER_ID! ', os.getenv("CONTAINER_ID"))
    logger('CONTAINER_ID! ', os.getenv("CONTAINER_ID"))
    logger('CONTAINER_ID! ', os.getenv("CONTAINER_ID"))
    logger(f"TRANSCRIBE BATCH SIZE: {download_batch_size}")
    for i in range(0, download_batch_size):
        logger("===========================================")
        logger(f"    TRANSCRIBE BATCH - {i+1} of {download_batch_size}  ")
        logger("===========================================")
        # vod: Vod = transcribe(isDebug)
        result: Dict[Vod, bool] = transcribe(isDebug)
        vod = result["vod"]
        isPass = result["isPass"]
        logger(f"   (goTranscribeBatch) Finished Index {i}")
        logger(f"   (goTranscribeBatch) download_batch_size: {i+1}")
        logger(f"   (goTranscribeBatch) Time to download vid: {time.time() - start_time}")
        if result["isPass"]:
            completed_vods_list.append(vod)
        else:
            failed_vods_list.append(vod)
    elapsed_time = time.time() - start_time
    logger("FINISHED! TOTAL TIME RUNNING= " + str(elapsed_time))
    logger("FINISHED! TOTAL TIME RUNNING= " + str(elapsed_time))
    logger("FINISHED! TOTAL TIME RUNNING= " + str(elapsed_time))
    logger("Completed: ")
    for v in failed_vods_list:
        logger(f"FAILED: {v.channels_name_id} - {v.title} - id: {v.id}")
    for v in completed_vods_list:
        logger(f"COMPLETE: {v.channels_name_id} - {v.title} - id: {v.id}")
    logger("SLEEPING BC END & debug")
    time.sleep(100) 
    logger("gg ending")
    return "gg ending"

def transcribe(isDebug=False) -> Dict[Vod, bool]:
    # Setup. Get Vod
    vods_list = transcriber.getTodoFromDb()
    vod: Vod = vods_list[0] if len(vods_list) > 0 else None
    relative_path = None
    logger('IN THEORY, AUDIO TO TEXT THIS:')
    if not vod and not isDebug:
        logger("jk, vod is null, nothing to do. no audio2text_need")
        return None
    if isDebug:
        vod = getDebugVod(vod)
    logger(vod.print())

    # Set TranscrptStatus = "transcribing"
    transcriber.setSemaphoreDb(vod)

    # Do the transcribing
    try:
        vod.printDebug()
        relative_path = transcriber.downloadAudio(vod)
        # saved_caption_files = transcriber.doInsaneWhisperStuff(vod, relative_path, isDebug)
        saved_caption_files = Audio2Text.doWhisperStuff(vod, relative_path)

        transcripts_s3_key_arr = transcriber.uploadCaptionsToS3(saved_caption_files, vod)
        transcriber.setCompletedStatusDb(transcripts_s3_key_arr, vod)
        transcriber.deleteAudioS3(vod)
    except Exception as e:
        error_message = f"ERROR Transcribing vod: {e}"
        stack_trace = traceback.format_exc()
        logger(error_message + "\n" + stack_trace)
        vod.print()
        transcriber.unsetProcessingDb(vod)
        return {"vod": vod, "isPass": False}

    transcriber.cleanUpFiles(relative_path)
    logger("Finished step 3 Transcriber-Service")
    return {"vod": vod, "isPass": True}

def getDebugVod(vod: Vod):
    vod.print() if vod else logger("Null nod")
    # tuple =  ('2143646862', 'kaicenat', '⚔️100+ HR STREAM⚔️ELDEN RING⚔️CLICK HERE⚔️GAMER⚔️BIGGEST DWARF⚔️ELITE⚔️PRAY 4 ME⚔️', '78', '1:18', 39744, 'https://www.twitch.tv/videos/40792901', datetime.datetime(2013, 8, 2, 18, 26, 30), 'audio2text_need', 1, 'https://static-cdn.jtvnw.net/jtv_user_pictures/1d8cd548-04fa-49fb-bfcd-f222f73482b6-profile_image-70x70.png', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/kaicenat/2143646862/100%252B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.opus', '-1', 'English')
    tuple =  ('40792901', 'nmplol', 'And you will know my name is the LORD', '78', '1:18', 39744, 'https://www.twitch.tv/videos/40792901', datetime.datetime(2013, 8, 2, 18, 26, 30), 'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/511e8d0d2a/nmplol_6356312704_6356312704/thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/nmplol/40792901/And_you_will_know_my_name_is_the_LORD-v40792901.opus', '-1', 'English')
    # tuple =  ('1964894986', 'jd_onlymusic', '夜市特攻隊「永和樂華夜市」ft. 陳老師', '732', '12:12', 1205, 'https://www.twitch.tv/videos/1964894986',datetime.datetime(2023, 10, 2, 18, 26, 30),'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d3vd9lfkzbru3h/e8c73b0847f78c0231fc_jd_onlymusic_40759279447_1698755215//thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/jd_onlymusic/1964894986/ft.-v1964894986.opus','-3', 'Chinese')
    # tuple =  ('28138895', 'lolgeranimo', 'The Geraniproject! I Love You Guys!!!', '1047', '17:26', 786, 'https://www.twitch.tv/videos/28138895',datetime.datetime(2023, 10, 2, 18, 26, 30),'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d3vd9lfkzbru3h/e8c73b0847f78c0231fc_jd_onlymusic_40759279447_1698755215//thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/lolgeranimo/28138895/The_Geraniproject_I_Love_You_Guys-v28138895.opus','-2', 'English')
    Id, ChannelNameId, Title, Duration, DurationString,ViewCount,WebpageUrl,StreamDate, TranscriptStatus, Priority, Thumbnail,TodoDate,S3Audio,ChanCurrentRank,Language  = tuple
    vod = Vod(id=Id, title=Title, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, todo_date=TodoDate, stream_date=StreamDate, s3_audio=S3Audio, language=Language)
    return vod