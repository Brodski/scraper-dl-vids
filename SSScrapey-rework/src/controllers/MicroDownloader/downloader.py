from datetime import datetime
from io import BytesIO
import sys
from dotenv import load_dotenv
from models.Vod import Vod
from pathlib import Path
from typing import List
import boto3
import json
import MySQLdb
import os
import re
import time
import traceback
import urllib
# import yt_dlp
import subprocess
import requests
import re
from controllers.MicroDownloader.errorEnum import Errorz
from utils.emailer import sendEmail
import logging
from utils.logging_config import LoggerConfig

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()


# load_dotenv()
# import env_file as env_varz
from env_file import env_varz

def getConnection():
    connection = MySQLdb.connect(
        db      = env_varz.DATABASE,
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        port    = int(env_varz.DATABASE_PORT),
        autocommit  = False,
    )
    return connection

# Logic below determins which Todo/highest_priority_vod
# Get last "5" recent vods from EVERY channel. 
# Take from the most popular channel
# Does NOT care about status, eg 'todo', 'downloading' ect
def getTodoFromDatabase(i, isDebug=False) -> List[Vod]:
    return getTodoFromDatabase_aux(i, 'todo', isDebug)

def getCompressNeedFromDatabase(i, isDebug=False) -> List[Vod]:
    return getTodoFromDatabase_aux(i, "audio_need_opus", isDebug)

def getTodoFromDatabase_aux(i, tr_status, isDebug=False) -> List[Vod]:
    highest_priority_vod = None #
    resultsArr: List[Vod] = []
    connection = getConnection()
    results = None
    # maxVodz = env_varz.DWN_QUERY_PER_RECENT <- old-old
    # maxVodz = env_varz.NUM_VOD_PER_CHANNEL <- old
    maxVodz = env_varz.PREP_NUM_VOD_PER_CHANNEL
    reach_back = 9
    try:
        with connection.cursor() as cursor:
            sql = f"""  
                    SELECT 
                        Vods.*,
                        Channels.CurrentRank
                    FROM Vods
                    JOIN Channels ON Vods.ChannelNameId = Channels.NameId
                    WHERE Vods.TodoDate >= NOW() - INTERVAL 8 DAY
                        AND Vods.TranscriptStatus = '{tr_status}'
                    ORDER BY Channels.CurrentRank ASC, Vods.TodoDate DESC;
                """
            # BELOW. 
            # sql = f"""  SELECT 
            #                 subquery.*
            #             FROM (
            #                 SELECT 
            #                     Vods.*,
            #                     Channels.CurrentRank,
            #                     ROW_NUMBER() OVER (
            #                         PARTITION BY Vods.ChannelNameId 
            #                         ORDER BY Channels.CurrentRank ASC, Vods.TodoDate DESC
            #                     ) as rn
            #                 FROM Vods 
            #                 JOIN Channels ON Vods.ChannelNameId = Channels.NameId
            #                 ) AS subquery 
            #             WHERE subquery.rn <= {maxVodz}
            #             ORDER BY CurrentRank
            #         """
            cursor.execute(sql)
            results = cursor.fetchall()
            # column_names = [desc[0] for desc in cursor.description]
            # Nice to uncomment when updating vod properties
            # print("    (getTodoFromDatabase) vod_ column_names")
            # logger.debug(column_names)
    except Exception as e:
        logger.error(f"    (getTodoFromDatabase) An error occurred: {e}")
        return []
    finally:
        connection.close()
    for vod_ in results:
        # Tuple unpacking
        # Id, ChannelNameId, Title, Duration, DurationString, TranscriptStatus, StreamDate, TodoDate, DownloadDate, TranscribeDate, S3Audio, S3CaptionFiles, WebpageUrl, Model, Priority, Thumbnail, ViewCount, S3Thumbnails,         ChanCurrentRank, RowNum  = vod_
        Id, ChannelNameId, Title, Duration, DurationString, TranscriptStatus, StreamDate, TodoDate, DownloadDate, TranscribeDate, S3Audio, S3CaptionFiles, WebpageUrl, Model, Priority, Thumbnail, ViewCount, S3Thumbnails,         ChanCurrentRank  = vod_
        vod = Vod(id=Id, title=Title, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, todo_date=TodoDate, stream_date=StreamDate, s3_audio=S3Audio,  s3_caption_files=S3CaptionFiles, transcribe_date=TranscribeDate, s3_thumbnails=S3Thumbnails, duration=Duration, duration_string=DurationString)
        resultsArr.append(vod)
        logger.info(f"resultsArr length! = {len(resultsArr)}")
    return resultsArr

    #Recall, results arr is sorted by priority via smart sql query
    highest_priority_vod: Vod = None
    for vod in resultsArr:
        if vod.transcript_status == "todo":
            highest_priority_vod = vod
            break

    ###############
    # DEBUG STUFF #
    ###############
    if i == 0: # i comes from parameter :/ onlly used in this line
        for vod in resultsArr:
            logger.debug(f"todos, in order of priority - {vod.channels_name_id}: prio {vod.priority}, {vod.id} - {vod.transcript_status}")
        logger.debug("")
    if isDebug:
        # highest_priority_vod = Vod(id="2143646862", channels_name_id="kaicenat", transcript="todo", priority=-1, channel_current_rank=-1) # (Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
        # highest_priority_vod = Vod(id="2017842017", channels_name_id="fps_shaka", transcript="todo", priority=0, channel_current_rank="-1") # (Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
        highest_priority_vod = Vod(id="40792901", channels_name_id="nmplol", transcript="todo", priority=-1, channel_current_rank=-1) # (Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
        logger.debug("DEBUG highest_priority_vod is :" + vod.channels_name_id, vod.id)
        # highest_priority_vod.print()
    return highest_priority_vod

def lockVodDb(vod: Vod, isDebug=False):
    logger.debug("LOCKING VOD DB: " + str(vod.id))
    connection = getConnection()
    transcript_dl_status = "downloading"
    try:
        with connection.cursor() as cursor:
            sql = f"SELECT Id, ChannelNameId, TranscriptStatus FROM Vods WHERE Id = {vod.id};"
            cursor.execute(sql)
            result = cursor.fetchone()  # Use fetchone() since we expect only one row for a specific id
            logger.debug(f"GOT! {sql}")
            # id = result[0]
            # channel_name_id = result[1]
            # transcript_status = result[2]
            if (result is None or result[2] != "todo") and isDebug != True:
                return False
            sql = """
                UPDATE Vods
                SET TranscriptStatus = %s
                WHERE Id = %s;
                """
            values = (transcript_dl_status, vod.id)
            affected_count = cursor.execute(sql, values)
            connection.commit()
            logger.debug(f"locked: {values}")
        return True
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        connection.rollback()
        raise
        # return False
    finally:
        connection.close()

def unlockVodDb(vod: Vod):
    logger.debug("    (unlockVodDb) UNLOCKING VOD DB: " + str(vod.id))
    connection = getConnection()
    revert_to = "todo"
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE Vods SET TranscriptStatus = %s WHERE id = %s"
            cursor.execute(sql, (revert_to, vod.id))
            connection.commit()
        return True
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def isVodDownloadable(vod: Vod):
    logger.debug(" ---- downloadPreCheck ----")
    vidUrl = "https://www.twitch.tv/videos/" + vod.id
    pattern = r"Video \d+ does not exist"
    yt_dlp_cmd = [
        'yt-dlp', vidUrl, '--dump-json',
    ]
    try:
        meta, stderr, returncode = _execSubprocCmd(yt_dlp_cmd)
        if "HTTP Error 403" in stderr or "You must be logged into an account that has access to this subscriber-only" in stderr:
            logger.error("Failed b/c 403. Probably private or sub only.")
            return Errorz.UNAUTHORIZED_403
        if re.search(pattern, stderr):
            logger.error("Failed b/c 'that content is unavailable'. Probably deleted")
            return Errorz.DELETED_404
        meta = json.loads(meta)
        duration = meta['duration']
        if duration > 86400: # 86400 sec = 24 hours
            return Errorz.TOO_BIG
    except Exception as e:
        logger.error("Failed to get vid's metadata!: " + vidUrl + " : " + str(e))
        traceback.print_exc()
    return True

def downloadTwtvVidFAST(vod: Vod, is_hls_retry=False):
    # yt-dlp==2023.3.4 WORKS LOCALLY ON WINDOWS
    # yt-dlp==2023.12.30 FAILS LOCALLY WINDOWS
    logger.info("000000000000                     00000000000000000")
    logger.info("000000000000 downloadTwtvVidFAST 00000000000000000")
    logger.info("000000000000                     00000000000000000")
    # TODO Temporarily disabling to try it out
    is_downloadable = isVodDownloadable(vod)
    if is_downloadable in (Errorz.TOO_BIG, Errorz.DELETED_404, Errorz.UNAUTHORIZED_403):
        return is_downloadable, 0

    #
    # Format paths and direct where to download file
    #
    start_time = time.time()
    main_script_path = sys.argv[0]
    absolute_path = os.path.realpath(main_script_path)
    app_root = os.path.dirname(absolute_path)
    app_root = os.path.normpath(app_root)
    output_local_dir = os.path.normpath("assets/audio") # TODO!!!!!!!!!!
    vidUrl = "https://www.twitch.tv/videos/" + vod.id

    output_template = os.path.join(app_root, output_local_dir, '%(title)s-%(id)s.%(ext)s')
    # output_template = 'C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework/assets/audio/%(title)s-%(id)s.%(ext)s'

    yt_dlp_cmd = [
        'yt-dlp', vidUrl,
        # *(["--hls-prefer-ffmpeg"] if is_hls_retry else []),
        *(['--downloader', 'm3u8:ffmpeg'] if is_hls_retry else []),
        '--dump-json',
        '--output', output_template,
        '--format', 'worst', 
        '--quiet',
        '--no-simulate', #unique to yt-dlp via command line
        '--restrict-filenames', 
        '--audio-quality', '0',
        '--concurrent-fragments', '100',
        *(["--no-progress"] if env_varz.ENV != "local" else []),
        *(["--force-overwrites"] if env_varz.ENV == "local" else []),
        *(["--no-continue"] if env_varz.ENV == "local" else []),
    ]

    # How to trim video without downloading it entirely  https://github.com/yt-dlp/yt-dlp/issues/2220
    if str(env_varz.DWN_IS_SHORT_DEV_DL) == "True" or env_varz.DWN_IS_SHORT_DEV_DL == True:
        yt_dlp_cmd.append('--download-sections')
        yt_dlp_cmd.append('*0:00-10:00') # download only first 10 min

    try:
        logger.debug(f"     YT_DLP: downloading - {vod.channels_name_id}, vodId: {vod.id} ")
        logger.debug("     YT_DLP: downloading url: " + vidUrl)
        logger.debug("\n     yt_dlp_cmd: " + str(yt_dlp_cmd))
        logger.debug("")
        metax, stderr, returncode = _execSubprocCmd(yt_dlp_cmd)
        meta = json.loads(metax)
        if returncode == 1 and "ERROR: Initialization fragment found after media fragments, unable to download" in stderr:
            logger.info(f"ERROR! with yt_dlp :( Retrying with 'hls' -> returncode={returncode}. stderr={stderr}")
            return downloadTwtvVidFAST(vod, True)
    except Exception as e:
        logger.error("    (dlTwtvVid) Failed to extract vid!!: " + vidUrl + " : " + str(e))
        traceback.print_exc()
        raise
    runtime = time.time() - start_time
    logger.info('\n    (dlTwtvVid) Download complete: time (seconds)=' + str(int(runtime)))
    logger.info('    (dlTwtvVid) Download complete: time (seconds)=' + str(int(runtime)))
    logger.info('    (dlTwtvVid) Download complete: time (seconds)=' + str(int(runtime)))
    return meta, runtime
    

# def convertVideoToSmallAudio(meta):
def convertVideoToSmallAudio(filepath):
    # filepath = C:\Users\SHAAAZAM\scraper-dl-vids\assets\audio\Calculated-v5057810.mp3
    
    start_time = time.time()

    last_dot_index = filepath.rfind('.')
    inFile = "file:" + filepath[:last_dot_index] + ".mp4" 
    outFile = "file:" + filepath[:last_dot_index] + ".opus" #opus b/c of the ffmpeg cmd below

    if env_varz.DWN_IS_SKIP_COMPRESS_AUDIO == True or env_varz.DWN_IS_SKIP_COMPRESS_AUDIO == "True":
        logger.debug("DWN_IS_SKIP_COMPRESS_AUDIO==False, not compressing Audio!")
        outFile = inFile
        return outFile, 0

    # https://superuser.com/questions/1422460/codec-and-setting-for-lowest-bitrate-ffmpeg-output
    ffmpeg_command = [ 'ffmpeg', '-y', '-i',  inFile, '-c:a', 'libopus', '-ac', '1', '-ar', '16000', '-b:a', '10K', '-vbr', 'constrained', '-application', 'voip', '-compression_level', '5', outFile ]
    
    logger.debug("    compressing Audio....\n")
    logger.debug(str(ffmpeg_command))
    _execSubprocCmd(ffmpeg_command)

    runtime_secs = time.time() - start_time    
    logger.debug("\n    run time (secs) = " + str(int(runtime_secs)) + "\n")
    return outFile, runtime_secs


def _execSubprocCmd(ffmpeg_command):
    try:
        # stdoutput, stderr, returncode = yt_dlp.utils.Popen.run(ffmpeg_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        process = subprocess.run(
            ffmpeg_command,
            text=True,              # get output as str instead of bytes
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        stdoutput = process.stdout
        stderr = process.stderr
        returncode = process.returncode
        # logger.debug(stdoutput)
        # logger.debug("    (exec) stderr:")
        # logger.debug(stderr)
        logger.debug("    (exec) returncode:")
        logger.debug(returncode)
        # stdoutput = stdoutput if stdoutput not in ("", None) else stderr
        return stdoutput, stderr, int(returncode)
    except subprocess.CalledProcessError as e:
        logger.error("Failed to run ffmpeg command:")
        logger.error(e)
        traceback.print_exc()
        raise
        return False


def removeNonSerializable(meta):
    def is_json_serializable(obj):
        try:
            json.dumps(obj)
            return True
        except (TypeError, OverflowError):
            return False
    to_delete = []
    for key, val in meta.items():
        if key == "requested_downloads":
            whitlist_properties = ["format_id","url","manifest_url","tbr","ext","fps","protocol","width","height","vcodec","acodec","dynamic_range","resolution","aspect_ratio","filesize_approx","video_ext","audio_ext","vbr","abr","format","epoch","_filename","__finaldir","filepath" ]            
            for item in meta['requested_downloads']:
                removeNonSerializable(item)
        if not is_json_serializable(val):
            # logger.debug("deleting:" + str(key))
            to_delete.append(key)
    for d in to_delete: # FFmpegFixupM3u8PP is not serializable, adding this semi annoying logic so i never need to look at this agian
        del meta[d]
    return meta





#
# Uploads: channels/vod-audio/lck/2023-04-18/576354726/metadta.json
# Uploads: channels/vod-audio/lck/2023-06-02/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.mp3
#
def uploadAudioToS3_v2(downloaded_metadata, outfile, vod: Vod):
    logger.info("000000000000                 00000000000000000")
    logger.info("000000000000 uploadAudioToS3 00000000000000000")
    logger.info("000000000000                 00000000000000000")

    ### Pretty sure I did something stupid and convoluted here 2 years ago, with the keys and names ###
    caption_keybase = env_varz.S3_CAPTIONS_KEYBASE + vod.channels_name_id + "/" + vod.id
    vod_title = os.path.basename(outfile)
    vod_encode = urllib.parse.quote(vod_title)
    s3fileKey = caption_keybase + "/" + vod_encode
    s3metaKey = caption_keybase + "/metadata.json"
    outfile_aux = outfile[5:]
    logger.debug("    uploading channel: " + vod.channels_name_id)
    logger.debug("    vod_id:" + vod.id)
    logger.debug("    meta.get(fulltitle)= " + downloaded_metadata.get('fulltitle'))
    logger.debug("    s3fileKey= " + s3fileKey)
    # logger.debug(json.dumps(downloaded_metadata, default=lambda o: o.__dict__))
    s3 = boto3.client('s3')
    try:
        if env_varz.DWN_IS_SKIP_COMPRESS_AUDIO == "False" or env_varz.DWN_IS_SKIP_COMPRESS_AUDIO == False:
            logger.info("SKIPPING THE UPLOAD B/C WE ARE LOCAL")
            logger.info("SKIPPING THE UPLOAD B/C WE ARE LOCAL")
            logger.info("SKIPPING THE UPLOAD B/C WE ARE LOCAL")
            logger.info("SKIPPING THE UPLOAD B/C WE ARE LOCAL")
            s3.upload_file(os.path.abspath(outfile_aux), env_varz.BUCKET_NAME, s3fileKey, ExtraArgs={ 'ContentType': 'audio/mpeg'})
        s3.put_object(Body=json.dumps(downloaded_metadata, default=lambda o: o.__dict__), ContentType="application/json; charset=utf-8", Bucket=env_varz.BUCKET_NAME, Key=s3metaKey)
        return s3fileKey
    except Exception as e:
        logger.error("oops! failed mp3 or metadata upload " + str(e))
        raise
        # return None
    

def updateVods_Db(downloaded_metadata, vod: Vod, s3fileKey, json_s3_img_keys):
    def getTitle(meta):
        if meta.get('title'):
            title = meta.get('title')
        elif meta.get('fulltitle'):
            title = meta.get('fulltitle')
        else: 
            title = vod_id
        return title
    vod_id              = vod.id
    title               = getTitle(downloaded_metadata)
    duration            = downloaded_metadata.get('duration')
    duration_string     = downloaded_metadata.get('duration_string')
    view_count          = downloaded_metadata.get('view_count')
    webpage_url         = downloaded_metadata.get('webpage_url')
    thumbnail           = downloaded_metadata.get('thumbnail')
    stream_epoch        = int(downloaded_metadata.get('timestamp'))
    # transcript_status   = "audio_need_opus" if env_varz.DWN_IS_SKIP_COMPRESS_AUDIO in (True, "True") else "audio2text_need" 
    transcript_status   = "audio2text_need" 

    vod.duration = int(duration)

    connection = getConnection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE Vods
                SET Title = %s,
                    Duration = %s,
                    DurationString = %s,
                    ViewCount = %s,
                    WebpageUrl = %s,
                    Thumbnail = %s,
                    TranscriptStatus = %s,
                    StreamDate = FROM_UNIXTIME(%s),
                    DownloadDate = NOW(),
                    S3Audio = %s,
                    S3Thumbnails =%s
                WHERE Id = %s;
                """
            values = (title, duration, duration_string, view_count, webpage_url, thumbnail, transcript_status, stream_epoch, s3fileKey, json.dumps(json_s3_img_keys), vod_id)
            affected_count = cursor.execute(sql, values)
            logger.debug("    (updateVods_Db) Updated " + vod_id + ". affected_counf= " + str(affected_count))
            connection.commit()
            return title, duration_string
    except Exception as e:
        logger.error(f"    (updateVods_Db) Error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()

# Take the twitch url and cleverly modifies their naming convension to compress/expand it to what I want
def updateImgs_Db(downloaded_metadata, vod: Vod) -> dict[str, str]:
    caption_keybase = env_varz.S3_CAPTIONS_KEYBASE + vod.channels_name_id + "/" + vod.id # channels/vod-audio/gamesdonequick/2035111776/

    s3 = boto3.client('s3')

    thumbnail = downloaded_metadata.get('thumbnail')

    json_s3_img_keys = {}

    ################
    # Save default #
    ################
    try:
        response = requests.get(thumbnail)
        response.raise_for_status() 
        if response.status_code == 200 and 'image' in response.headers['Content-Type']:

            # Make name/key for s3
            content_type = response.headers['Content-Type']
            ext = content_type.split('/')[-1]
            fname_default = extract_name_from_url(thumbnail)
            img_key = f"{caption_keybase}/images/{fname_default}.{ext}"

            # Save image to s3
            image_data = BytesIO(response.content)
            s3.upload_fileobj(image_data, env_varz.BUCKET_NAME, img_key, ExtraArgs={'ContentType': content_type})
            
            # used later
            json_s3_img_keys['original'] = img_key
            
            logger.debug("     Saved *Default* thumbnail: " + img_key)
    except Exception as e:
        logger.error(f"An error occurred: {e}")


    #######################
    # Save good thumbnail #
    #######################
    width_thumbnail_in_my_s3 = 350
    width_thumbnail_in_my_s3 = 300

    # 1 Regex for basic algebra
    pattern = r'-([0-9]+)x([0-9]+)\.'
    replacement = r'-\2x\1.'
    match = re.search(pattern, thumbnail)
    width =  float(match.group(1))
    height = float(match.group(2))

    # 2 Basic algebra to get new width, new height
    if width == 0 or height == 0:
        width = 300
        height = 168
    aspect_ratio = width / height
    multliple_width_by_this_to_get_desired_compressed_width = width_thumbnail_in_my_s3 / width
    new_width = int(multliple_width_by_this_to_get_desired_compressed_width * width)
    new_height = int(new_width / aspect_ratio)

    # 3 New url via regex
    replacement = fr'-{new_width}x{new_height}.'
    new_thumbnail = re.sub(pattern, replacement, thumbnail)
    # 'https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/ed8c9e0388e846f9f5f3_geranimo_315294119415_1763235443//thumb/thumb0-300x168.jpg'
    logger.debug("     new_thumbnail-small: " + new_thumbnail)

    ###################
    # Save compressed #
    ###################
    response = None
    try:
        response = requests.get(new_thumbnail)
        response.raise_for_status() 
        if response.status_code == 200 and 'image' in response.headers['Content-Type']:

            # Name the s3 key
            fname_mod = extract_name_from_url(new_thumbnail)
            img_key = f"{caption_keybase}/images/{fname_mod}"

            # Save it in s3
            image_data = BytesIO(response.content)
            content_type = response.headers['Content-Type']
            s3.upload_fileobj(image_data, env_varz.BUCKET_NAME, img_key, ExtraArgs={'ContentType': content_type})
            
            json_s3_img_keys['small'] = img_key

            logger.debug("     Saved Small thumbnail ")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        the_msg = ''.join(traceback.format_stack())

        subject = f"Downloader {os.getenv('ENV')} - Failed image 'compression' on {vod.channels_name_id} : {vod.id}"
        msg = f"Attempted but failed thumbnail={thumbnail} on {vod.channels_name_id} : {vod.id}. \n\nStack:\n\n {the_msg}"
        logger.error(msg)
        sendEmail(subject, msg)

    logger.debug("     json_s3_img_keys" + str(json_s3_img_keys))
    return json_s3_img_keys


# Uses my sick compressing server
# return { "original": "https://...", "small": ... }
# def updateImgs_Db_old(downloaded_metadata, vod: Vod) -> dict[str, str]:
#     caption_keybase = env_varz.S3_CAPTIONS_KEYBASE + vod.channels_name_id + "/" + vod.id # channels/vod-audio/gamesdonequick/2035111776/
#     s3 = boto3.client('s3')
#     thumbnail = downloaded_metadata.get('thumbnail')

#     json_s3_img_keys = {}

#     # Save default
#     try:
#         width_thumbnail_in_my_s3 = 350

#         response = requests.get(thumbnail)
#         response.raise_for_status() 
#         if response.status_code == 200 and 'image' in response.headers['Content-Type']:
#             content_type = response.headers['Content-Type']
#             ext = content_type.split('/')[-1]
#             fname_default = extract_name_from_url(thumbnail)
#             img_key = f"{caption_keybase}/images/{fname_default}.{ext}"
#             image_data = BytesIO(response.content)
#             s3.upload_fileobj(image_data, env_varz.BUCKET_NAME, img_key, ExtraArgs={'ContentType': content_type})
            
#             json_s3_img_keys['original'] = img_key
            
#             logger.debug("     thumbnail: " + thumbnail)
#             logger.debug("     img_key: " + img_key)
#             logger.debug("     Saved Default thumbnail ")
#     except requests.exceptions.RequestException as e:
#         logger.debug(f"An error occurred: {e}")

#     # Save compressed
#     response = None
#     compresser_endpoint = env_varz.DWN_URL_MINI_IMAGE
#     data = { 'imageUrl': thumbnail, 'width': width_thumbnail_in_my_s3, }
#     headers = { 'Content-Type': 'application/json' }
#     try:
#         response = requests.post(compresser_endpoint, data=json.dumps(data), headers=headers)
#         response.raise_for_status() 
#         content_type = response.headers['Content-Type']
#         fname_mod = response.headers.get('X-Bski-Filename') or response.headers.get('x-bski-filename')
#         img_key = f"{caption_keybase}/images/{fname_mod}"
#         if response.status_code == 200 and 'image' in response.headers['Content-Type']:
#             image_data = BytesIO(response.content)
#             s3.upload_fileobj(image_data, env_varz.BUCKET_NAME, img_key, ExtraArgs={'ContentType': content_type})
            
#             json_s3_img_keys['small'] = img_key

#             logger.debug("     fname_mod:" + fname_mod)
#             logger.debug("     thumbnail: " +thumbnail)
#             logger.debug("     img_keymod: " + img_key)
#             logger.debug("     Saved Small thumbnail ")
#     except requests.exceptions.RequestException as e:
#         logger.debug(f"An error occurred: {e}")

#     logger.debug("     json_s3_img_keys" + json_s3_img_keys)
#     return json_s3_img_keys

def extract_name_from_url(url):
    try:
        filename_default = None
        last_idx_dot = url.rfind(".")
        last_idx_slash = url.rfind("/")

        # Ends in a file type eg www.bigboy.com/image/of/bigboy.jpg
        if last_idx_dot > last_idx_slash:
            last_idx_junk_before = url.rfind("/", 0, last_idx_dot)
            filename_default = url[last_idx_junk_before + 1:last_idx_dot]

        # else www.bigboy.com/image/of/bigboy
        else:
            filename_default = url[last_idx_slash + 1:]

        # atm: `filename_defalt = thumb0-90x60.jpg `
        filename_default = re.sub(r'[^a-zA-Z0-9]', '', filename_default)
        filename_default =  re.sub(r'(0x0|00x0)$', '', filename_default)
        filename_default = filename_default if filename_default else "imagefile"
        filename_default = filename_default[:20]
        return filename_default
    except Exception as e:
        logger.error("oops")
        logger.error(e)
        traceback.print_stack()
        return "imagefile"


def updateErrorVod(vod: Vod, error_msg: str):
    logger.debug(f"Something failed with downloadTwtvVid2. {vod.channels_name_id}, vodId: {vod.id}. Error type: {error_msg}")
    connection = getConnection()
    t_status = error_msg
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
        logger.error(f"Error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()

def cleanUpDownloads(downloaded_metadata):
    if env_varz.ENV == "local":
        logger.debug("Local Env. NOT cleaning up files")
        return
    extenstions = ['.mp3', '.mp4', '.opus']
    filename = downloaded_metadata.get('_filename') 
    last_dot_index = filename.rfind('.')
    for ex in extenstions:
        file_ = filename[:last_dot_index] + ex
        file_abs = os.path.abspath(file_)
        if os.path.exists(file_abs) and os.path.isfile(file_abs):
            os.remove(file_abs)
            logger.debug('Deleted: ' + str(file_abs))
    return 
