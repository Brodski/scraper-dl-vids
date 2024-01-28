import datetime
from models.Vod import Vod
from typing import List
import controllers.MicroTranscriber.transcriber as transcriber
import json
import os
import time
import boto3
import urllib.parse
import urllib.request
import env_file as env_varz
# import controllers.MicroTranscriber.cloudwatch as cloudwatch
from controllers.MicroTranscriber.cloudwatch import Cloudwatch 


# def logger():
#     pass
# logger = Cloudwatch.log
def logger():
    pass
logger = Cloudwatch.log

def goTranscribeBatch(isDebug=False):
    logger("Hello sucker! " + str(time.time()))
    # logger("Hello sucker!", time.time())
    download_batch_size = int(env_varz.WHSP_BATCH_SIZE)
    logger(f"DOWNLOAD BATCH SIZE: {download_batch_size}")
    for i in range(0, download_batch_size):
        logger("===========================================")
        logger(f"    DOWNLOAD BATCH - {i+1} of {download_batch_size}  ")
        logger("===========================================")
        x = transcribe(isDebug)
        logger(f"Finished Index {i}")
        logger(f"download_batch_size: {i+1}")
    logger("FINISHED! " + str(time.time()))
    return x



def transcribe(isDebug=False):
    # Setup. Get Vod
    vods_list = transcriber.getTodoFromDb()
    vod = vods_list[0] if len(vods_list) > 0 else None
    relative_path = None
    logger('IN THEORY, AUDIO TO TEXT THIS:')
    if not vod and not isDebug:
        logger("jk, vod is null, nothing to do. no audio2text_need")
        return "NOTHING TO DO NO VODS READY"
    if isDebug:
        vod = getDebugVod(vod)
    vod.print()

    # Set TranscrptStatus = "transcribing"
    transcriber.setSemaphoreDb(vod)

    # Do the transcribing
    try:
        logger('downloading vod ...')
        vod.printDebug()
        relative_path = transcriber.downloadAudio(vod)
        saved_caption_files = transcriber.doWhisperStuff(vod, relative_path)
        transcripts_s3_key_arr = transcriber.uploadCaptionsToS3(saved_caption_files, vod)
        transcriber.setCompletedStatusDb(transcripts_s3_key_arr, vod)
        transcriber.deleteAudioS3(vod)
    except Exception as e:
        logger(f"ERROR Transcribing vod: {e}")
        vod.print()
        transcriber.unsetProcessingDb(vod)

    transcriber.cleanUpFiles(relative_path)
    logger("Finished step 3 Transcriber-Service")
    return "Finished step 3 Transcriber-Service"

def getDebugVod(vod: Vod):
    vod.print() if vod else logger("Null nod")
    tuple =  ('40792901', 'nmplol', 'And you will know my name is the LORD', '78', '1:18', 39744, 'https://www.twitch.tv/videos/40792901', datetime.datetime(2013, 8, 2, 18, 26, 30), 'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/511e8d0d2a/nmplol_6356312704_6356312704/thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/nmplol/40792901/And_you_will_know_my_name_is_the_LORD-v40792901.opus', '-1', 'English')
    # tuple =  ('1964894986', 'jd_onlymusic', '夜市特攻隊「永和樂華夜市」ft. 陳老師', '732', '12:12', 1205, 'https://www.twitch.tv/videos/1964894986',datetime.datetime(2023, 10, 2, 18, 26, 30),'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d3vd9lfkzbru3h/e8c73b0847f78c0231fc_jd_onlymusic_40759279447_1698755215//thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/jd_onlymusic/1964894986/ft.-v1964894986.opus','-3', 'Chinese')
    # tuple =  ('28138895', 'lolgeranimo', 'The Geraniproject! I Love You Guys!!!', '1047', '17:26', 786, 'https://www.twitch.tv/videos/28138895',datetime.datetime(2023, 10, 2, 18, 26, 30),'audio2text_need', 1, 'https://static-cdn.jtvnw.net/cf_vods/d3vd9lfkzbru3h/e8c73b0847f78c0231fc_jd_onlymusic_40759279447_1698755215//thumb/thumb0-90x60.jpg', datetime.datetime(2023, 12, 27, 5, 37), 'channels/vod-audio/lolgeranimo/28138895/The_Geraniproject_I_Love_You_Guys-v28138895.opus','-2', 'English')
    Id, ChannelNameId, Title, Duration, DurationString,ViewCount,WebpageUrl,StreamDate, TranscriptStatus, Priority, Thumbnail,TodoDate,S3Audio,ChanCurrentRank,Language  = tuple
    vod = Vod(id=Id, title=Title, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, todo_date=TodoDate, stream_date=StreamDate, s3_audio=S3Audio, language=Language)
    return vod