import traceback
import types
from controllers.MicroTranscriber.audio2Text_faster_whisper import Audio2Text 
from models.Vod import Vod
# from transformers import pipeline
# from transformers.utils import is_flash_attn_2_available
from typing import Dict, List
# from whisper.utils import get_writer
import boto3
from env_file import env_varz
# import faster_whisper
import json
# import langcodes
import MySQLdb
import os
import time
# import torch
import urllib.parse
import urllib.request
import logging
from utils.logging_config import LoggerConfig
from controllers.MicroTranscriber.utils import TOO_BIG_LENGTH
from utils.emailer import MetadataShitty

# logger = Cloudwatch.log
def logger():
    pass
logger: logging.Logger = LoggerConfig("micro", env_varz.WHSP_IS_CLOUDWATCH == "True").get_logger()


def getConnectionDb():
    connection = MySQLdb.connect(
        db      = env_varz.DATABASE,
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        port    = int(env_varz.DATABASE_PORT),
        autocommit  = False,
    )
    return connection

def getTodoFromDb():
    logger.debug("     (getTodoFromDb) Getting Todo's from Db")
    resultsArr = []
    connection = getConnectionDb()
    reach_back = 9
    last_7_days = "WHERE Vods.StreamDate >= NOW() - INTERVAL 8 DAY"
    is_recent = True
    try:
        with connection.cursor() as cursor:
            sql = f"""
                WITH RankedVods AS (
                    SELECT 
                        Vods.*, 
                        Channels.CurrentRank AS ChanCurrentRank, 
                        Channels.Language AS ChanLanguage,
                        ROW_NUMBER() OVER (PARTITION BY Vods.ChannelNameId ORDER BY Vods.StreamDate DESC) AS RowNum
                    FROM Vods
                    JOIN Channels ON Vods.ChannelNameId = Channels.NameId
                    {last_7_days if is_recent else ""}
                )
                SELECT *
                FROM RankedVods
                WHERE RowNum <= {reach_back} AND TranscriptStatus= 'audio2text_need'
                ORDER BY ChanCurrentRank ASC, StreamDate DESC;
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
    except Exception as e:
        logger.error(f"Error occurred (getTodoFromDb): {e}")
        connection.rollback()
    finally:
        connection.close()
    logger.debug("'''''''''''''''''''''''''")
    logger.debug("'''''''''''''''''''''''''")
    logger.debug("'''''''''''''''''''''''''")
    for counterz, vod_ in enumerate(results):
        # Tuple unpacking
        Id, ChannelNameId, Title, Duration, DurationString, TranscriptStatus, StreamDate, TodoDate, DownloadDate, TranscribeDate, S3Audio, S3CaptionFiles, WebpageUrl, Model, Priority, Thumbnail, ViewCount, S3Thumbnails,         ChanCurrentRank, ChanLanguage, RowNum  = vod_
        vod = Vod(id=Id, title=Title, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, todo_date=TodoDate, download_date = DownloadDate, stream_date=StreamDate, s3_audio=S3Audio, language=ChanLanguage, s3_caption_files=S3CaptionFiles, transcribe_date=TranscribeDate, s3_thumbnails=S3Thumbnails, duration=Duration, duration_string=DurationString)
        resultsArr.append(vod)
        # logger.debug(f"{vod.channels_name_id} - {vod.stream_date}")
    
    # HERE TODO
    # HERE TODO
    # LAZY FIX B/C THE SQL QUERY IS UGLY SINCE Duration IS A STRING/VARCHAR
    if env_varz.WHSP_IS_BIG_FILES_ENABLED == False or env_varz.WHSP_IS_BIG_FILES_ENABLED == "False":
        logger.debug("Removing long files - env_varz.WHSP_IS_BIG_FILES_ENABLED=" + str(env_varz.WHSP_IS_BIG_FILES_ENABLED))
        logger.debug("Removing long files ....")
        # resultsArr[:] = [vod for vod in resultsArr if int(vod.duration) >= 64800]

        # logger.debug("Todo candidates")
        keep = []
        for vod in resultsArr:
            if int(vod.duration) < TOO_BIG_LENGTH:
                keep.append(vod)
                # logger.debug(f"{vod.channels_name_id} - {vod.stream_date}")

        resultsArr[:] = keep



    return resultsArr


def unsetSemaphoreDb(vod: Vod):
    logger.debug("UNLOCKING VOD: " + str(vod.id))
    connection = getConnectionDb()
    t_status = "audio2text_need"
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE Vods
                SET TranscriptStatus = %s
                WHERE Id = %s;
                """
            values = (t_status, vod.id)
            affected_count = cursor.execute(sql, values)
            connection.commit()
    except Exception as e:
        logger.error(f"Error occurred (unsetProcessingDb): {e}")
        connection.rollback()
    finally:
        connection.close()


def setSemaphoreDb(vod: Vod):
    logger.debug("LOCKING VOD: " + str(vod.id))
    connection = getConnectionDb()
    t_status = "transcribing"
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE Vods
                SET TranscriptStatus = %s
                WHERE Id = %s;
                """
            values = (t_status, vod.id)
            affected_count = cursor.execute(sql, values)
            connection.commit()
    except Exception as e:
        logger.error(f"Error occurred (setSemaphoreDb): {e}")
        connection.rollback()
    finally:
        connection.close()

def setCompletedStatusDb(transcripts_s3_key_arr: List[str], vod: Vod):
    logger.debug(vod.print())
    connection = getConnectionDb()
    t_status = "completed"
    transcripts_keys = json.dumps(transcripts_s3_key_arr)
    logger.debug("   (setCompletedStatusDb) transcripts_keys:" + str( transcripts_keys))
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE Vods
                SET TranscriptStatus = %s,
                Model = %s,
                S3CaptionFiles = %s,
                TranscribeDate = NOW()
                WHERE Id = %s;
                """
            values = (t_status, env_varz.WHSP_MODEL_SIZE, transcripts_keys, vod.id)
            affected_count = cursor.execute(sql, values)
            connection.commit()
    except Exception as e:
        logger.error(f"Error occurred (setCompletedStatusDb): {e}")
        connection.rollback()
    finally:
        connection.close()

########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################

def downloadAudio(vod: Vod):
    print("######################################")
    print("             downloadAudio            ")
    print("######################################")

    WHSP_A2T_ASSETS_AUDIO="./assets/audio/"

    audio_url = f"{env_varz.BUCKET_DOMAIN}/{urllib.parse.quote(vod.s3_audio)}"

    audio_name = os.path.basename(audio_url)  # A trick to get the file name. eg) audio_url="https://[...].com/Calculated-v5057810.mp3" ---> audio_name="Calculated-v5057810.mp3"
    
    relative_filename = WHSP_A2T_ASSETS_AUDIO +  audio_name
    logger.debug("audio_url: " + str( audio_url))
    logger.debug("audio_name: " + str( audio_name))
    
    # Check if file is already present
    if os.path.exists(relative_filename):
        logger.debug(f"File already exists: {relative_filename}")
        return relative_filename

    try:
        relative_path, headers  = urllib.request.urlretrieve(audio_url, relative_filename) # audio_url = Calculated-v123123.ogg
    except:
        stack_trace = traceback.format_exc()
        logger.error("    (downloadAudio) FAILED!!!! (audio_url, relative_filename) =" + str( (audio_url, relative_filename)))
        logger.error(stack_trace)
        logger.error("    (downloadAudio) FAILED sleeping 1 min for some reason....")
        time.sleep(60)
        return None

    return relative_path



def uploadCaptionsToS3(saved_caption_files: List[str], vod: Vod):
    logger.debug("XXXXXXXXXXXXXX  uploadCaptionsToS3  XXXXXXXXXXXXXX")
    logger.debug("    (uploadCaptionsToS3) channel: " + vod.channels_name_id)
    logger.debug("    (uploadCaptionsToS3) vod.id: " + vod.id) 
    logger.debug("    (uploadCaptionsToS3) vod.title: " + vod.title) 

    s3 = boto3.client('s3')
    transcripts_s3_key_arr = []
    for filename in saved_caption_files:
        file_abs = os.path.abspath(env_varz.WHSP_A2T_ASSETS_CAPTIONS + filename)
            #   channels/vod-audio/nmplol/40792901/And_you_will_know_my_name_is_the_LORD-v40792901.opus
        audio_url = f"{env_varz.S3_CAPTIONS_KEYBASE}/{urllib.parse.quote(vod.s3_audio)}"
        s3CapFileKey = env_varz.S3_CAPTIONS_KEYBASE + vod.channels_name_id + "/" + vod.id + "/" + filename

        content_type = ''
        if file_abs[-4:] == '.txt':
            content_type = 'text/plain; charset=utf-8'
        if file_abs[-5:] ==  '.json':
            content_type = 'application/json; charset=utf-8'
        if file_abs[-4:] ==  '.vtt':
            content_type = 'text/vtt; charset=utf-8'
        try:
            s3.upload_file(file_abs, env_varz.BUCKET_NAME, s3CapFileKey, ExtraArgs={ 'ContentType': content_type })
            transcripts_s3_key_arr.append(s3CapFileKey)
            Audio2Text.completed_uploaded_tscripts.append(f"{env_varz.BUCKET_DOMAIN}/{s3CapFileKey}")
        except Exception as e:
            logger.error(f"failed to upload: {file_abs}. Error {str(e)}")

    return transcripts_s3_key_arr 


def deleteAudioS3(vod: Vod):
    logger.debug(f" ====  Deleting vod: {vod.channels_name_id} {vod.id} ==== ")
    if os.getenv("ENV") != "local":
        s3 = boto3.client('s3')
        response = s3.delete_object(Bucket=env_varz.BUCKET_NAME, Key=vod.s3_audio)
    else:
        logger.debug(f"jk skipping delete - local")

def deleteAudioLocally(relative_path: str):
    try:
        file_abs = os.path.abspath(relative_path)
        if os.getenv("ENV") != "local":
            os.remove(file_abs)
            logger.debug("    (deleteAudioLocally) FILE DELETED")
    except Exception as e:
        logger.error('     (deleteAudioLocally) failed to run cleanUpFiles() on: ',  relative_path)
        logger.error(str(e))
    return 


# def getFromFancyMap(d: dict[int, list]):
#     # https://chatgpt.com/c/69278b8e-856c-8332-9475-66ce608d2298
#     # data: Dict[int, List[Vod]] = {
#     #     1: [a1,a2,a3],
#     #     2: [b1,b2,b3,b4,b5,b6],
#     #     3: [c1,c2],
#     # }
#     # outputs -> 1 column, 2nd column, 3rd, ....
#     # outputs -> a1,b1,c1, a2,b2,c2, a3,b3, b4, b5, b6   
#     keys = d.keys()
#     max_len = max(len(d[k]) for k in keys)
#     for x in range(max_len): # x = column
#         for y in keys: # y = row
#             row = d[y]
#             if x < len(row):
#                 yield row[x] 

# def convertToFancyMap(vod_list: List[Vod]) -> Dict[int, List[Vod]]:
#     sub_list = []
#     magical_ordered_map = {}
#     previous = vod_list[0].channels_name_id # initialize
#     idx_rank = 0
#     for i, vod in enumerate(vod_list):
#         current = vod.channels_name_id
#         if previous != current:
#             magical_ordered_map[idx_rank] = sub_list
#             previous = current
#             sub_list = []
#             idx_rank += 1
#         sub_list.append(vod)
    
#     # Add the last group
#     magical_ordered_map[idx_rank + 1] = sub_list

#     mega_count = 0
#     for key, v_list in magical_ordered_map.items():
#         logger.debug(f"----------- {str(key)} -----------")
#         for i, v in enumerate(v_list):
#             v: Vod = v
#             # logger.debug(i, " - ", v.channels_name_id, v.id, v.stream_date)
#             logger.debug(f"{i} - {v.channels_name_id} {v.id} {v.stream_date}")
#             mega_count += 1
#     logger.debug("Total = " + str(mega_count))
#     return magical_ordered_map

    # "Transformers now supports natively BetterTransformer optimizations ... no need to use `model.to_bettertransformers()` Details: https://huggingface.co/docs/transformers/perf_infer_gpu_one#flashattention-and-memory-efficient-attention-through-pytorchs-scaleddotproductattention."
    # if not is_flash_attn_2_available() or better_transformer:
    #     pipe.model = pipe.model.to_bettertransformer()
