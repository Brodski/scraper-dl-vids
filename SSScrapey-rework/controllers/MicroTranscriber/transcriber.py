from models.Vod import Vod
from typing import List
from whisper.utils import get_writer
import boto3
import datetime
import env_file as env_varz
import faster_whisper
import json
import langcodes
import MySQLdb
import os
import time
import torch
import urllib.parse
import urllib.request
def getConnectionDb():
    connection = MySQLdb.connect(
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        db      = env_varz.DATABASE,
        autocommit  = True,
        ssl_mode    = "VERIFY_IDENTITY",
        ssl         = { "ca": env_varz.SSL_FILE } # See https://planetscale.com/docs/concepts/secure-connections#ca-root-configuration to determine the path to your operating systems certificate file.
    )
    return connection

def getTodoFromDb():
    print("Getting Todo's from Db")
    resultsArr = []
    connection = getConnectionDb()
    
    try:
        with connection.cursor() as cursor:
            sql = """ 
                    SELECT Vods.*, Channels.CurrentRank AS ChanCurrentRank, Channels.Language AS ChanLanguage
                    FROM Vods
                    JOIN Channels ON Vods.ChannelNameId = Channels.NameId
                    WHERE Vods.TranscriptStatus = 'audio2text_need'
                    ORDER BY Channels.CurrentRank ASC, Vods.DownloadDate ASC
                    # ORDER BY Channels.CurrentRank ASC, Vods.UploadDate ASC
                    LIMIT 100
                """
            cursor.execute(sql)
            results = cursor.fetchall()
    except Exception as e:
        print(f"Error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()
    for vod_ in results:
        # Tuple unpacking
        Id, ChannelNameId, Title, Duration, DurationString, ViewCount, WebpageUrl, TranscriptStatus, Priority, Thumbnail, TodoDate, S3Audio, Model, DownloadDate, StreamDate, ChanCurrentRank, Language  = vod_
        vod = Vod(id=Id, title=Title, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, todo_date=TodoDate, stream_date=StreamDate, s3_audio=S3Audio, language=Language)
        resultsArr.append(vod)
    print("resultsArr")
    print(resultsArr)
    return resultsArr

def setSemaphoreDb(vod: Vod):
    connection = getConnectionDb()
    t_status = "processing"
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE Vods
                SET TranscriptStatus = %s
                WHERE Id = %s;
                """
            values = (t_status, vod.id)
            affected_count = cursor.execute(sql, values)
    except Exception as e:
        print(f"Error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()

        
def downloadAudio(vod: Vod):
    print("######################################")
    print("             downloadAudio            ")
    print("######################################")
    audio_url = f"{env_varz.BUCKET_DOMAIN}/{vod.s3_audio}"

    audio_name = os.path.basename(audio_url) # A trick to get the file name. eg) filename = "Calculated-v5057810.mp3"
    audio_name_encode = urllib.parse.quote(audio_name)
    meta_url = audio_url.replace(audio_name, "metadata.json")
    audio_url = audio_url.replace(audio_name, audio_name_encode)    
    relative_filename = env_varz.WHSP_A2T_ASSETS_AUDIO +  audio_name_encode
    bucket_domain = env_varz.BUCKET_DOMAIN
    relative_path, headers  = urllib.request.urlretrieve(audio_url, relative_filename) # audio_url = Calculated-v123123.ogg
    print("    (downloadAudio) bucket_domain=" + bucket_domain)
    print("    (downloadAudio) audio_url=" + str(audio_url))
    print("    (downloadAudio) audio_name=" + str(audio_name))
    print("    (downloadAudio) audio_name_encode=" + str(audio_name_encode))
    print("    (downloadAudio) meta_url=" + str(meta_url))
    print("    (downloadAudio) relative_filename=" + str(relative_filename))    
    print("    (downloadAudio) relative_path: " + relative_filename)

    return relative_path

def doWhisperStuff(vod: Vod, relative_path: str):
    print("Starting WhisperStuff!")
    def get_language_code(full_language_name):
        try:
            language_code = langcodes.find(full_language_name).language
            return language_code
        except:
            return None
    lang_code = get_language_code(vod.language)
    model_size = (env_varz.WHSP_MODEL_SIZE + ".en") if lang_code == "en" else env_varz.WHSP_MODEL_SIZE
    compute_type = env_varz.WHSP_COMPUTE_TYPE
    cpu_threads = int(env_varz.WHSP_CPU_THREADS)

    file_abspath = os.path.abspath(relative_path) # if relative_path =./assets/audio/ft.-v1964894986.opus then => file_abspath = C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\And_you_will_know_my_name_is_the_LORD-v40792901.opus
    file_name = os.path.basename(relative_path) # And_you_will_know_my_name_is_the_LORD-v40792901.opus

    # model = faster_whisper.WhisperModel(model_size, device="cuda", compute_type="int8", cpu_threads=8)
    model = faster_whisper.WhisperModel(model_size, compute_type=compute_type,  cpu_threads=cpu_threads) # 4 default

    start_time = time.time()

    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("    Channel=" + vod.channels_name_id)
    print("    s3_audio=" + vod.s3_audio)
    print("    relative_path=" + relative_path)
    print("    file_abspath=" + file_abspath)
    print("    file_name: " + file_name)
    print("    torch.cuda.is_available(): " + str(torch.cuda.is_available()))
    print("    model_size: " + model_size)

    # segments, info = model.transcribe(audio_abs_path, language="en")
    # segments, info = model.transcribe(audio_abs_path, language="en", condition_on_previous_text=False, vad_filter=True)
    segments, info = model.transcribe(file_abspath, language=lang_code, condition_on_previous_text=False, vad_filter=True, beam_size=2, best_of=2) # vad_filter = something to prevents bugs. long loops being stuck
    

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    result = {  "segments": [] }
    for segment in segments: # generator()
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        result["segments"].append({
            "start" : segment.start,
            "end" :   segment.end,
            "text" :  segment.text,
        })

    saved_caption_files = writeCaptionsLocally(result, file_name)
    end_time = time.time() - start_time

    print("========================================")
    print("Complete!")
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    print()
    print("run time =" + str(end_time))
    print()
    print("Saved files: " + str(saved_caption_files))
    print()
    print("model_size: " + model_size)
    print()
    print("========================================")

    return saved_caption_files


def writeCaptionsLocally(result, audio_basename):
    FILE_EXTENSIONS_TO_SAVE = ["json", "vtt", "txt"]
    saved_caption_files = []
    abs_path = os.path.abspath(audio_basename) 
    print("------   WRITE FILE   ------")
    print("abs_path: " + abs_path)
    print("audio_basename: " + audio_basename)
    filename_without_ext , file_extension = os.path.splitext(audio_basename) # [Calculated-v5057810, .mp3]

    for ext in FILE_EXTENSIONS_TO_SAVE:
        srt_writer = get_writer(ext, env_varz.WHSP_A2T_ASSETS_CAPTIONS)
        srt_writer(result, audio_basename + ext)

        caption_file = filename_without_ext  + '.' + ext
        saved_caption_files.append(caption_file)
        print("Wrote - " + ext + " - " + caption_file)

    return saved_caption_files


def uploadCaptionsToS3(saved_caption_files: List[str], vod: Vod):
    print ("XXXXXXXXXXXXXX  uploadCaptionsToS3  XXXXXXXXXXXXXX")
    print("    (uploadCaptionsToS3) channel: " + vod.channels_name_id)
    print("    (uploadCaptionsToS3) vod_id: " + vod.id) 

    s3 = boto3.client('s3')

    for filename in saved_caption_files:
        try:
            file_abs = os.path.abspath(env_varz.WHSP_A2T_ASSETS_CAPTIONS + filename)
            s3CapFileKey = env_varz.S3_CAPTIONS_KEYBASE + vod.channels_name_id + "/" + vod.id + "/" + filename

            print("    (uploadCaptionsToS3) filename: " + filename) 
            print("    (uploadCaptionsToS3) file_abs: " + file_abs)
            print("    (uploadCaptionsToS3) s3CapFileKey: " + s3CapFileKey)
            print("     s3CapFileKey: " + s3CapFileKey)
            content_type = ''
            if file_abs[-4:] == '.txt':
                content_type = 'text/plain; charset=utf-8'
            if file_abs[-5:] ==  '.json':
                content_type = 'application/json; charset=utf-8'
            if file_abs[-4:] ==  '.vtt':
                content_type = 'text/vtt; charset=utf-8'
            s3.upload_file(file_abs, env_varz.BUCKET_NAME, s3CapFileKey, ExtraArgs={ 'ContentType': content_type })
            # return "channels/vod-audio/lolgeranimo/1856310873/How_to_Climb_on_Adc_So_washed_up_i_m_clean_-_hellofresh-v1856310873.vtt"
        except:
            print("SHIT WENT WRONGGGGGGGGGG!@")
        return s3CapFileKey 
    
def setCompletedStatusDb(vod: Vod):
    print("updating database ...")
    vod.print()
    connection = getConnectionDb()
    t_status = "completed"
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE Vods
                SET TranscriptStatus = %s,
                Model = %s
                WHERE Id = %s;
                """
            values = (t_status, vod.id, env_varz.WHSP_MODEL_SIZE)
            affected_count = cursor.execute(sql, values)
    except Exception as e:
        print(f"Error occurred: {e}")
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
    except Exception as e:
        print(f"Error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()

def cleanUpFiles(relative_path: str):
    print("cleanUpFiles")
    print("relative_path: " + relative_path)
    try:
        file_abs = os.path.abspath(relative_path)
        print("cleanUpFiles - file_abs= " + file_abs)
        if os.getenv("ENV") != "local":
            print("DELETING IT!!!!!!!")
            os.remove(file_abs)
    except Exception as e:
        print('failed to run cleanUpFiles() on: ' + relative_path)
        print(str(e))
    return 
