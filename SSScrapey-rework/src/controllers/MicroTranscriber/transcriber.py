import traceback
import types
from controllers.MicroTranscriber.cloudwatch import Cloudwatch 
from models.Vod import Vod
# from transformers import pipeline
# from transformers.utils import is_flash_attn_2_available
from typing import List
# from whisper.utils import get_writer
import boto3
import env_file as env_varz
# import faster_whisper
import json
# import langcodes
import MySQLdb
import os
import time
# import torch
import urllib.parse
import urllib.request
# from controllers.MicroTranscriber.Writer import Writer

def logger():
    pass
logger = Cloudwatch.log


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
    logger("     (getTodoFromDb) Getting Todo's from Db")
    resultsArr = []
    connection = getConnectionDb()
    reach_back = 2
    try:
        with connection.cursor() as cursor:
            # sql = """ 
            #         SELECT Vods.*, Channels.CurrentRank AS ChanCurrentRank, Channels.Language AS ChanLanguage
            #         FROM Vods
            #         JOIN Channels ON Vods.ChannelNameId = Channels.NameId
            #         WHERE Vods.TranscriptStatus = 'audio2text_need'
            #         ORDER BY Channels.CurrentRank ASC, Vods.DownloadDate DESC
            #         LIMIT 100
            #     """
            
            # use a Common Table Expression (CTE) 
            sql = f"""
                WITH RankedVods AS (
                    SELECT 
                        Vods.*, 
                        Channels.CurrentRank AS ChanCurrentRank, 
                        Channels.Language AS ChanLanguage,
                        ROW_NUMBER() OVER (PARTITION BY Vods.ChannelNameId ORDER BY Vods.StreamDate DESC) AS RowNum
                    FROM Vods
                    JOIN Channels ON Vods.ChannelNameId = Channels.NameId
                )
                SELECT *
                FROM RankedVods
                WHERE RowNum <= {reach_back} AND TranscriptStatus= 'audio2text_need'
                ORDER BY ChanCurrentRank ASC, DownloadDate DESC;
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
    except Exception as e:
        logger(f"Error occurred (getTodoFromDb): {e}")
        connection.rollback()
    finally:
        connection.close()
    for counterz, vod_ in enumerate(results):
        # Tuple unpacking
        Id, ChannelNameId, Title, Duration, DurationString, TranscriptStatus, StreamDate, TodoDate, DownloadDate, TranscribeDate, S3Audio, S3CaptionFiles, WebpageUrl, Model, Priority, Thumbnail, ViewCount, S3Thumbnails,         ChanCurrentRank, ChanLanguage, RowNum  = vod_
        vod = Vod(id=Id, title=Title, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, todo_date=TodoDate, stream_date=StreamDate, s3_audio=S3Audio, language=ChanLanguage, s3_caption_files=S3CaptionFiles, transcribe_date=TranscribeDate, s3_thumbnails=S3Thumbnails)
        resultsArr.append(vod)
        # logger(f"     (getTodoFromDb) {counterz} vod: {vod.channels_name_id}: {vod.title} - {vod.id}")
    return resultsArr

def setSemaphoreDb(vod: Vod):
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
        logger(f"Error occurred (setSemaphoreDb): {e}")
        connection.rollback()
    finally:
        connection.close()








def downloadAudio(vod: Vod):
    logger("######################################")
    logger("             downloadAudio            ")
    logger("######################################")

    WHSP_A2T_ASSETS_AUDIO="./assets/audio/"

    audio_url = f"{env_varz.BUCKET_DOMAIN}/{urllib.parse.quote(vod.s3_audio)}"

    audio_name = os.path.basename(audio_url)  # A trick to get the file name. eg) audio_url="https://[...].com/Calculated-v5057810.mp3" ---> audio_name="Calculated-v5057810.mp3"
    
    relative_filename = WHSP_A2T_ASSETS_AUDIO +  audio_name
    logger("    (downloadAudio) vod.s3_audio:", vod.s3_audio)
    logger("    (downloadAudio) audio_url", audio_url)
    logger("    (downloadAudio) audio_name", audio_name)    
    logger("    (downloadAudio) relative_filename", relative_filename)    
    try:
        relative_path, headers  = urllib.request.urlretrieve(audio_url, relative_filename) # audio_url = Calculated-v123123.ogg
    except:
        stack_trace = traceback.format_exc()
        logger("    (downloadAudio) FAILED!!!! (audio_url, relative_filename) =", (audio_url, relative_filename))
        logger(stack_trace)
        logger("    (downloadAudio) sleeping 1.5 min for some reason....")
        time.sleep(90) # 1.5 min
        return None

    return relative_path

# def doInsaneWhisperStuff(vod: Vod, relative_path: str, isDebug=False):
#     print("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
#     print("    xxxxxxx     doInsaneWhisperStuff()      xxxxxxx")
#     print("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
#     def get_language_code(full_language_name):
#         try:
#             language_code = langcodes.find(full_language_name).language
#             return language_code
#         except:
#             return None
#     lang_code = get_language_code(vod.language)
#     model_size_insane = env_varz.WHSP_MODEL_SIZE # "openai/whisper-tiny"
#     compute_type = env_varz.WHSP_COMPUTE_TYPE
#     cpu_threads = int(env_varz.WHSP_CPU_THREADS)

#     my_device = "cuda:0" if torch.cuda.is_available() else "cpu"

#     file_abspath = os.path.abspath(relative_path) # if relative_path =./assets/audio/ft.-v1964894986.opus then => file_abspath = C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\And_you_will_know_my_name_is_the_LORD-v40792901.opus
#     file_name = os.path.basename(relative_path) # And_you_will_know_my_name_is_the_LORD-v40792901.opus
#     start_time = time.time()

#     logger("    (doInsaneWhisperStuff) Channel=" + vod.channels_name_id)
#     logger("    (doInsaneWhisperStuff) model_size_insane: " + model_size_insane)
#     logger("    (doInsaneWhisperStuff) torch.cuda.is_available(): " + str(torch.cuda.is_available()))
#     logger("    (doInsaneWhisperStuff) is_flash_attn_2_available(): " + str(is_flash_attn_2_available()))
#     logger("    (doInsaneWhisperStuff) Running it ...")


#     pipe = pipeline( # https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.pipeline
#         "automatic-speech-recognition",
#         model=model_size_insane, 
#         torch_dtype=torch.float16,
#         device=my_device,
#         model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
#     )
#     # https://github.com/Vaibhavs10/insanely-fast-whisper/issues/6
#     generate_kwargs = {
#         "language": lang_code,
#         # "temperature": 0.2,
#         "repetition_penalty": 1.25, # 1 = default = no penatlty
#         "task": "transcribe",
#     }

#     if isDebug and False:
#         outputs =  {'text': " Let's see, this is PTR. Crazy ketchup come! Alright maybe clang because I want to be part of the cake again I'm glad we're you can do it. Imagine that smoking, Kelly? It's more like needles! Not really against smoking anything Got someone out...I know it didn't heal you. You're on me hard! I got my wallet These alley i'm blinding Oh wow don' even hit him The files bug Yeah are ya been healing with me? No The foul's bug. Yeah, you been helping me? Why are What're your doing what do we You Where aren't Are What are you doing? what're ya doin'? Why aren't y'all u goin'! You mean, you second shit?! It's a good one, I i gonna do this by myself? l don't even need your help. Don t leave me here to help! Let him take care of you and then he just got absolutely brilliant Just fucking kill be one of them! Oh my god... What's up, a fowler? WHAT'S UP?! Aaaaaahhhhhh", 'chunks': [{'timestamp': (0.0, 7.0), 'text': " Let's see, this is PTR."}, {'timestamp': (7.02, 8.5), 'text': ' Crazy ketchup come!'}, {'timestamp': (8.52, 11.52), 'text': ' Alright maybe clang because I want to be part of the cake again'}, {'timestamp': (11.54, 13.67), 'text': " I'm glad we're you can do it."}, {'timestamp': (14.67, 15.67), 'text': ' Imagine that smoking, Kelly?'}, {'timestamp': (17.67, 23.67), 'text': " It's more like needles! Not really against smoking anything"}, {'timestamp': (25.13, 25.63), 'text': " Got someone out...I know it didn't heal you."}, {'timestamp': (26.43, 26.53), 'text': " You're on me hard!"}, {'timestamp': (27.33, 28.93), 'text': ' I got my wallet'}, {'timestamp': (30.03, 30.63), 'text': " These alley i'm blinding"}, {'timestamp': (31.63, 32.33), 'text': " Oh wow don' even hit him"}, {'timestamp': (33.13, 34.76), 'text': " The files bug Yeah are ya been healing with me? No The foul's bug."}, {'timestamp': (36.76, 37.26), 'text': ' Yeah, you been helping me?'}, {'timestamp': (38.46, 38.56), 'text': ' Why are'}, {'timestamp': (40.56, 40.58), 'text': " What're your doing"}, {'timestamp': (41.52, 42.16), 'text': ' what do we'}, {'timestamp': (43.44, 43.84), 'text': ' You'}, {'timestamp': (45.2, 46.07), 'text': " Where aren't Are What are you doing? what're ya doin'?"}, {'timestamp': (47.17, 48.37), 'text': " Why aren't y'all u goin'!"}, {'timestamp': (50.07, 54.87), 'text': ' You mean, you second shit?!'}, {'timestamp': (58.33, 58.35), 'text': " It's a good one, I i gonna do this by myself?"}, {'timestamp': (60.33, 60.35), 'text': " l don't even need your help."}, {'timestamp': (62.35, 62.37), 'text': ' Don t leave me here to help!'}, {'timestamp': (66.33, 66.35), 'text': ' Let him take care of you and then he just got absolutely brilliant'}, {'timestamp': (69.52, 71.02), 'text': ' Just fucking kill be one of them!'}, {'timestamp': (72.02, 72.04), 'text': ' Oh my god...'}, {'timestamp': (74.02, 74.04), 'text': " What's up, a fowler?"}, {'timestamp': (75.04, 76.04), 'text': " WHAT'S UP?!"}, {'timestamp': (77.04, None), 'text': ' Aaaaaahhhhhh'}]}
#     else:
#         outputs = pipe(
#             file_abspath,
#             chunk_length_s=16, # 16 works pretty good # stide = chunk / 6
#             batch_size=24,
#             # return_timestamps="word",
#             return_timestamps=True,
#             generate_kwargs = generate_kwargs
#         )
    
#     logger("outputs length:", len(outputs))
#     # logger(outputs)
#     logger()
#     logger()

#     saved_caption_files = write_files(outputs, file_name)

#     end_time = time.time() - start_time

#     logger("========================================")
#     logger("Complete!")
#     logger(f"Detected language {lang_code}!")
#     logger()
#     logger("run time =" + str(end_time))
#     logger()
#     logger("Saved files: " + str(saved_caption_files))
#     logger()
#     logger("model_size_insane: " + model_size_insane)
#     logger()
#     logger("========================================")
#     return saved_caption_files

# def write_files(outputs, filename):
#     FILE_EXTENSIONS_TO_SAVE = ["json", "vtt", "txt", "srt"]
#     saved_caption_files = []
#     filename_without_ext , file_extension = os.path.splitext(filename) # [Calculated-v5057810, .mp3]

#     for ext in FILE_EXTENSIONS_TO_SAVE:
#         writer: Writer = Writer(ext)
#         writer.write(outputs, filename, env_varz.WHSP_A2T_ASSETS_CAPTIONS)
#         saved_caption_files.append(f"{filename_without_ext}.{ext}")

#     return saved_caption_files






def uploadCaptionsToS3(saved_caption_files: List[str], vod: Vod):
    logger("XXXXXXXXXXXXXX  uploadCaptionsToS3  XXXXXXXXXXXXXX")
    logger("    (uploadCaptionsToS3) channel: " + vod.channels_name_id)
    logger("    (uploadCaptionsToS3) vod.id: " + vod.id) 
    logger("    (uploadCaptionsToS3) vod.title: " + vod.title) 

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
        except Exception as e:
            logger(f"failed to upload: {file_abs}. Error {str(e)}")

    return transcripts_s3_key_arr 

def setCompletedStatusDb(transcripts_s3_key_arr: List[str], vod: Vod):
    logger(vod.print())
    connection = getConnectionDb()
    t_status = "completed"
    transcripts_keys = json.dumps(transcripts_s3_key_arr)
    logger("   (setCompletedStatusDb) transcripts_keys:", transcripts_keys)
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
        logger(f"Error occurred (setCompletedStatusDb): {e}")
        connection.rollback()
    finally:
        connection.close()

def unsetProcessingDb(vod: Vod):
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
        logger(f"Error occurred (unsetProcessingDb): {e}")
        connection.rollback()
    finally:
        connection.close()

def deleteAudioS3(vod: Vod):
    logger(f" ====  Deleting vod: {vod.channels_name_id} {vod.id} ==== ")
    if os.getenv("ENV") != "local":
        s3 = boto3.client('s3')
        response = s3.delete_object(Bucket=env_varz.BUCKET_NAME, Key=vod.s3_audio)

def cleanUpFiles(relative_path: str):
    try:
        file_abs = os.path.abspath(relative_path)
        if os.getenv("ENV") != "local":
            os.remove(file_abs)
            logger("     (cleanUpFiles) FILE DELETED")
    except Exception as e:
        logger('     (cleanUpFiles) failed to run cleanUpFiles() on: ',  relative_path)
        logger(str(e))
    return 



    # "Transformers now supports natively BetterTransformer optimizations ... no need to use `model.to_bettertransformers()` Details: https://huggingface.co/docs/transformers/perf_infer_gpu_one#flashattention-and-memory-efficient-attention-through-pytorchs-scaleddotproductattention."
    # if not is_flash_attn_2_available() or better_transformer:
    #     pipe.model = pipe.model.to_bettertransformer()
