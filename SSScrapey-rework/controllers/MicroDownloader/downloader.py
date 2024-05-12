from datetime import datetime
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
import subprocess
import time
import urllib
import yt_dlp
import subprocess
from controllers.MicroDownloader.errorEnum import Errorz


# load_dotenv()
import env_file as env_varz

def getConnection():

    connection = MySQLdb.connect(
        db      = env_varz.DATABASE,
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        port    = int(env_varz.DATABASE_PORT),
        autocommit  = False,
        # ssl_mode    = "VERIFY_IDENTITY",
        # ssl         = { "ca": env_varz.SSL_FILE } # See https://planetscale.com/docs/concepts/secure-connections#ca-root-configuration to determine the path to your operating systems certificate file.
    )
    return connection

# Logic below determins which Todo/highest_priority_vod
# Get last 5 recent vods from every channel. Take from the most popular channel
def getTodoFromDatabase(isDebug=False) -> Vod:
    highest_priority_vod = None #
    resultsArr = []
    connection = getConnection()
    maxVodz = env_varz.DWN_QUERY_PER_RECENT
    try:
        with connection.cursor() as cursor:
            sql = f"""  SELECT 
                            subquery.*
                        FROM (
                            SELECT 
                                Vods.*,
                                Channels.CurrentRank,
                                # ROW_NUMBER() OVER (PARTITION BY Vods.ChannelNameId ORDER BY TodoDate) as rn
                                ROW_NUMBER() OVER (PARTITION BY Vods.ChannelNameId ORDER BY Channels.CurrentRank ASC, Vods.TodoDate DESC) as rn
                            FROM Vods 
                            JOIN Channels ON Vods.ChannelNameId = Channels.NameId
                            # WHERE Vods.TranscriptStatus = 'todo'
                            ) AS subquery 
                        WHERE subquery.rn <= {maxVodz}
                        ORDER BY CurrentRank
                        """
# SELECT ass.* FROM (
#     SELECT 
#         V.ChannelNameId, 
#         V.StreamDate,
#         C.CurrentRank,
#         ROW_NUMBER() OVER (PARTITION BY V.ChannelNameId ORDER BY V.StreamDate DESC) as RowNum
#     FROM 
#         Vods V
#     INNER JOIN 
#         Channels C ON V.ChannelNameId = C.NameId
#     LEFT JOIN 
#         Rankings R ON V.ChannelNameId = R.ChannelNameId
# ) AS ass
# WHERE 
#     RowNum <= 2
# ORDER BY 
#     CurrentRank, ChannelNameId, StreamDate DESC;
            



# SELECT 
#     ass.* 
# FROM (
#     SELECT 
#         V.ChannelNameId, 
#         V.TodoDate,
#         C.CurrentRank,
#         RR.Ranking,
#         ROW_NUMBER() OVER (PARTITION BY V.ChannelNameId ORDER BY V.TodoDate DESC) as RowNum
#     FROM 
#         Vods V
#     INNER JOIN 
#         Channels C ON V.ChannelNameId = C.NameId
#     LEFT JOIN 
#         (
#             SELECT 
#                 ChannelNameId,
#                 Ranking,
#                 TodoDate
#             FROM (
#                 SELECT 
#                     R.ChannelNameId,
#                     R.Ranking,
#                     R.TodoDate,
#                     ROW_NUMBER() OVER (PARTITION BY R.ChannelNameId ORDER BY R.TodoDate DESC) AS RowNum
#                 FROM 
#                     Rankings R
#             ) AS RankedRankings
#             WHERE 
#                 RowNum = 1
#         ) AS RR ON V.ChannelNameId = RR.ChannelNameId
# ) AS ass
# WHERE 
#     RowNum <= 2
# ORDER BY 
#     ass.Ranking, ass.ChannelNameId, ass.TodoDate DESC;


            # sql = """   SELECT Vods.*, Channels.CurrentRank AS ChanCurrentRank
            #             FROM Vods
            #             JOIN Channels ON Vods.ChannelNameId = Channels.NameId
            #             WHERE Vods.TranscriptStatus = 'todo'
            #             # ORDER BY Channels.CurrentRank ASC, Vods.TodoDate ASC, Vods.Priority ASC
            #             ORDER BY Vods.TodoDate ASC, Channels.CurrentRank ASC, Vods.Priority ASC
            #             LIMIT 100
            #             """
            print("    (getTodoFromDatabase) sql:", sql)
            cursor.execute(sql)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            print ("    (getTodoFromDatabase) vod_ column_names")
            print(column_names)
    except Exception as e:
        print(f"    (getTodoFromDatabase) An error occurred: {e}")
        return []
    finally:
        connection.close()
    # print("    (getTodoFromDatabase) Vod candidates:")
    for vod_ in results:
        # Tuple unpacking
        Id, ChannelNameId, Title, Duration, DurationString, TranscriptStatus, StreamDate, TodoDate, DownloadDate, TranscribeDate, S3Audio, S3CaptionFiles, WebpageUrl, Model, Priority, Thumbnail, ViewCount,        ChanCurrentRank, rownum = vod_
        vod = Vod(id=Id, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, model=Model, todo_date=TodoDate, s3_caption_files=S3CaptionFiles, transcribe_date=TranscribeDate)
        # vod.print()
        resultsArr.append(vod)

    highest_priority_vod: Vod = None
    for vod in resultsArr:
        print(f"    (getTodoFromDatabase) todos, in order of priority - {vod.channels_name_id}: {vod.id}")
    #Recall, results arr is sorted by priority via smart sql query
    for vod in resultsArr:
        # vod.print()
        if vod.transcript_status == "todo":
            highest_priority_vod = vod
            break
    print("    (getTodoFromDatabase) highest_priority_vod:")
    if highest_priority_vod:
        print(f"    name: {highest_priority_vod.channels_name_id}")
        print(f"    id: {highest_priority_vod.id}")
        # highest_priority_vod.printDebug()
    if isDebug:
        # 'https://www.twitch.tv/videos/1783465374' # pro leauge
        # 'https://www.twitch.tv/videos/1791750006' # lolgera
        # 'https://www.twitch.tv/videos/1792255936' # sub only
        # 'https://www.twitch.tv/videos/1792342007' # live
        # 'www.twitch.tv/videos/28138895'
        highest_priority_vod = Vod(id="40792901", channels_name_id="nmplol", transcript="todo", priority=-1, channel_current_rank=-1) # (Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
        # highest_priority_vod = Vod(id="2017842017", channels_name_id="fps_shaka", transcript="todo", priority=0, channel_current_rank="-1") # (Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
        print("    (getTodoFromDatabase) DEBUG highest_priority_vod is now:")
        highest_priority_vod.print()
    return highest_priority_vod

# def getNeededVod_OLD(vods_list: List[Vod]):    
#     maxVodz = 2
#     print("[][][][][][][][][][][][][][][][][][][][]")
#     vods_dict_temp = {}
#     vods_dict = {}
#     for vod in vods_list:
#         vods_dict_temp.setdefault(vod.channels_name_id, []).append(vod)
#     for key in vods_dict_temp:
#         print(f"{key}: {vods_dict_temp[key]}")
#         for x in vods_dict_temp[key]:
#             x.print()
#         filtered_objects = [obj for obj in vods_dict_temp[key][:maxVodz] if obj.transcript_status == 'todo']
#         if filtered_objects:
#             vods_dict[key] = filtered_objects

#     keyHighestPrioChan = list(vods_dict.keys())[0]
#     vod: Vod = vods_dict[keyHighestPrioChan][0]
#     print("NEXT VOD IN THEORY")
#     vod.print()
#     return vod

def lockVodDb(vod: Vod, isDebug=False):
    print("    (lockVodDb) LOCKING VOD DB: " + str(vod.id))
    connection = getConnection()
    transcript_dl_status = "downloading"
    try:
        with connection.cursor() as cursor:
            sql = f"SELECT Id, ChannelNameId, TranscriptStatus FROM Vods WHERE Id = {vod.id};"
            cursor.execute(sql)
            result = cursor.fetchone()  # Use fetchone() since we expect only one row for a specific id
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
            print(f"    (lockVodDb) Set {vod.id} to 'downloading', affected_count: : {affected_count}")
            connection.commit()
        return True
    except Exception as e:
        print(f"Error occurred: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def isVodTooBig(vod: Vod):
    print(" ---- downloadPreCheck ----")
    vidUrl = "https://www.twitch.tv/videos/" + vod.id
    yt_dlp_cmd = [
        'yt-dlp', vidUrl, 
        '--dump-json',
    ]
    try:
        print("    (downloadPreCheck) YT_DLP: getting metadata ... " + vidUrl)
        meta = _execSubprocCmd(yt_dlp_cmd)
        meta = json.loads(meta)
        duration = meta['duration']
        print("    (downloadPreCheck) duration: " + str(duration))
        if duration > 86400: # 86400 sec = 24 hours
            return True
    except Exception as e:
        print ("Failed to get vid's metadata!: " + vidUrl + " : " + str(e))
    return False

def downloadTwtvVidFAST(vod: Vod): 
    print ("000000000000                     00000000000000000")
    print ("000000000000 downloadTwtvVidFAST 00000000000000000")
    print ("000000000000                     00000000000000000")
    if vod == None or vod.id == None:
        print("ERROR no vod")
        return
    if isVodTooBig(vod):
        return Errorz.TOO_BIG
    start_time = time.time()
    # format paths and direct where to download file
    main_script_path = sys.argv[0]
    absolute_path = os.path.realpath(main_script_path)
    app_root = os.path.dirname(absolute_path)
    app_root = os.path.normpath(app_root)
    output_local_dir = os.path.normpath("assets/audio") # TODO!!!!!!!!!!
    vidUrl = "https://www.twitch.tv/videos/" + vod.id

    output_template = os.path.join(app_root, output_local_dir, '%(title)s-%(id)s.%(ext)s')
    # output_template = 'C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework/assets/audio/%(title)s-%(id)s.%(ext)s'

    # How to trim video without downloading it entirely  https://github.com/yt-dlp/yt-dlp/issues/2220
    yt_dlp_cmd = [
                    'yt-dlp', vidUrl, 
                    '--dump-json',
                    '--output', output_template,
                    '--extract-audio', 
                    '--force-overwrites', # dev
                    '--no-continue', # dev
                    '--format', 'worst', 
                    '--quiet',
                    '--no-simulate', #unique to yt-dlp via command line
                    # '--parse-metadata', 'requested_downloads_filepath:%(filepath):',
                    '--audio-format', 'mp3', 
                    '--restrict-filenames', 
                    '--downloader', 'ffmpeg', 
                    '--audio-quality', '0',
                    '--no-progress' if env_varz.ENV != "local" else  ""   
                  ]
    # if env_varz.ENV != "local":
    #     yt_dlp_cmd.append('--no-progress')
    if env_varz.DWN_IS_SHORT_DEV_DL == "True":
        # download only first 669 seconds
        yt_dlp_cmd.append('--downloader-args')
        yt_dlp_cmd.append('ffmpeg_i: -ss 00 -to 669')

    try:
        print("    (dlTwtvVid) YT_DLP: downloading ... " + vidUrl)
        print("\n    (dlTwtvVid) yt_dlp_cmd: ", yt_dlp_cmd)
        print()
        meta = _execSubprocCmd(yt_dlp_cmd)
        meta = json.loads(meta)
    except Exception as e:
        print ("    (dlTwtvVid) Failed to extract vid!!: " + vidUrl + " : " + str(e))
        pattern = r"Video \d+ does not exist"
        if "HTTP Error 403" in str(e):
            print("Failed b/c 403. Probably private or sub only.")
            return Errorz.UNAUTHORIZED_403
        if re.search(pattern, str(e)):
            print("Failed b/c 'that content is unavailable'. Probably deleted")
            return Errorz.DELETED_404
        else:
            print ("Failed to extract vid!!: " + vidUrl + " : " + str(e))
            return Errorz.UNKNOWN

    print('    (dlTwtvVid) Download complete: time=' + str(time.time() - start_time))
    return meta
    

# 'API'  https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L137-L312
def downloadTwtvVid2(vod: Vod, isDownload=True): 
    if vod == None or vod.id == None:
        print("ERROR no vod")
        return
    start_time = time.time()
    output_local_dir = "assets/audio"
    output_local_dir = os.path.normpath("assets/audio") # TODO!!!!!!!!!!
    vidUrl = "https://www.twitch.tv/videos/" + vod.id
    main_script_path = sys.argv[0]
    absolute_path = os.path.realpath(main_script_path)
    app_root = os.path.dirname(absolute_path)

    print("  (dlTwtvVid) vidUrl= " + vidUrl)
    print("  (dlTwtvVid) app_root= " + str(app_root))
    output_template = os.path.join(app_root, output_local_dir, '%(title)s-%(id)s.%(ext)s')

    ydl_opts = {
        # Formatting info --> https://github.com/yt-dlp/yt-dlp#sorting-formats
        # 'format': 'worstaudio/Audio_Only/600/250/bestaudio/worstvideo/160p30',
        "outtmpl": output_template,
        "extractaudio": True,
        "format": "worst",
        "audioformat": "mp3",
        "restrictfilenames": True,
        # "audioformat": "worst",
        # "listformats": True,      # FOR DEBUGGING
        "quiet": True,
        # "download_ranges": "*0:00:00-0:00:30", # aka '--download_sections'
        # "download_ranges": "*10:15-inf", # aka '--download_sections'
        # "verbose": True,
        "noprogress": True if env_varz.ENV != "local" else False,
        "parse_metadata" "requested_downloads.filepath:%(filepath):"  # my custom  metadata field
        "overwrites": True,
        'downloader': 'ffmpeg',
        'downloader_args': {
            'ffmpeg_i': ['-ss', '300', '-to', '369']
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',        # https://trac.ffmpeg.org/wiki/Encode/MP3
        #     # 'preferredquality': '192',  # https://github.com/ytdl-org/youtube-dl/blob/195f22f679330549882a8234e7234942893a4902/youtube_dl/postprocessor/ffmpeg.py#L302
        }],
    }
    print("  x(dlTwtvVid) output_template ... " + output_template)
    print("  x(dlTwtvVid) downloading ... " + vidUrl)
    print("  x(dlTwtvVid) downloading ... " + vidUrl)
    print("  x(dlTwtvVid) downloading ... " + vidUrl)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print("  (dlTwtvVid) downloading ... " + vidUrl)
            meta = ydl.extract_info(vidUrl, download=isDownload) 
        except Exception as e:
            pattern = r"Video \d+ does not exist"
            if "HTTP Error 403" in str(e):
                print("Failed b/c 403. Probably private or sub only.")
                return "403"
            if re.search(pattern, str(e)):
                print("Failed b/c 'that content is unavailable'. Probably deleted")
                return "404"
            else:
                print ("Failed to extract vid!!: " + vidUrl + " : " + str(e))
                return None
    print('  (dlTwtvVid) Download complete: time=' + str(time.time() - start_time))
    print("CLASSIC")
    print("CLASSIC")
    print("CLASSIC")
    print("CLASSIC")
    print("CLASSIC")
    print(meta)
    return meta

def convertVideoToSmallAudio(meta):
    start_time = time.time()
    # filepath = meta.get('requested_downloads')[0].get('filepath')  
    filepath = meta.get('_filename') #C:\Users\SHAAAZAM\scraper-dl-vids\assets\audio\Calculated-v5057810.mp3

    last_dot_index = filepath.rfind('.')
    inFile = "file:" + filepath[:last_dot_index] + ".mp3" 
    if env_varz.DWN_COMPRESS_AUDIO == "True":
        outFile = "file:" + filepath[:last_dot_index] + ".opus" #opus b/c of the ffmpeg cmd below
    else:
        outFile = inFile
    
    # print("  (dlTwtvVid) filepath= "+filepath)
    # print("  (dlTwtvVid) inFile= "+inFile)
    # print("  (dlTwtvVid) outFile= "+outFile)

    # Debugging commands:
    # ffmpeg -i '.\Adc Academy - Informative Adc Stream - GrandMaster today？ [v1792628012].mp3' -c:a libopus -ac 1 -ar 16000 -b:a 33K -vbr constrained gera33k.opus
    # ffmpeg_command = [ 'ffmpeg', '-i', inFile, '-q:a', '0', '-map', 'a', inFile+'.mp3' ]
    # ffmpeg_command = [ 'ffmpeg', '-version' ]
    # ffmpeg_command = [ 'ffmpeg', '-y', '-i', inFile, '-filter:a', 'atempo=1.5', outFile ]

    # https://superuser.com/questions/1422460/codec-and-setting-for-lowest-bitrate-ffmpeg-output
    ffmpeg_command = [ 'ffmpeg', '-y', '-i',  inFile, '-c:a', 'libopus', '-ac', '1', '-ar', '16000', '-b:a', '10K', '-vbr', 'constrained', outFile ]
    if env_varz.DWN_COMPRESS_AUDIO == "True":
        print("    (convertVideoToSmallAudio): compressing Audio....")
        _execSubprocCmd(ffmpeg_command)

    time_diff = time.time() - start_time    
    print("    (convertVideoToSmallAudio): run time = ", str(time_diff))
    return meta, outFile

# def _execCmd(command):
#     print("    (exec2) _execCmd: starting subprocess!")
#     print("    (exec2) command=" + " ".join(command))
#     # print(command)
#     with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
#         output, errors = proc.communicate()

#         print("Output:", output.decode())
#         print("Errors:", errors.decode())
#         if proc.returncode != 0:
#             print("Command failed with return code", proc.returncode)
#     return output

def _execSubprocCmd(ffmpeg_command):
    try:
        # print("    (exec) Starting subprocess!")
        # print("    (exec) ffmpeg_command=" + " ".join(ffmpeg_command))
        stdoutput, stderr, returncode = yt_dlp.utils.Popen.run(ffmpeg_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        # print(stdoutput)
        # print("    (exec) stderr:")
        # print(stderr)
        # print("    (exec) returncode:")
        # print(returncode)
        return stdoutput
    except subprocess.CalledProcessError as e:
        print("Failed to run ffmpeg command:")
        print(e)
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
            # print("deleting:" + str(key))
            to_delete.append(key)
    for d in to_delete: # FFmpegFixupM3u8PP is not serializable, adding this semi annoying logic so i never need to look at this agian
        del meta[d]
    return meta





#
# Uploads: channels/vod-audio/lck/2023-04-18/576354726/metadta.json
# Uploads: channels/vod-audio/lck/2023-06-02/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.mp3
#
def uploadAudioToS3_v2(downloaded_metadata, outfile, vod: Vod):
    print ("000000000000                 00000000000000000")
    print ("000000000000 uploadAudioToS3 00000000000000000")
    print ("000000000000                 00000000000000000")

    # ext = downloaded_metadata.get("requested_downloads")[0].get('ext')
    caption_keybase = env_varz.S3_CAPTIONS_KEYBASE + vod.channels_name_id + "/" + vod.id
    vod_title = os.path.basename(outfile)
    vod_encode = urllib.parse.quote(vod_title)
    s3fileKey = caption_keybase + "/" + vod_encode
    s3metaKey = caption_keybase + "/metadata.json"
    outfile_aux = outfile[5:]
    print("    (uploadAudioToS3) uploading channel: " + vod.channels_name_id)
    print("    (uploadAudioToS3) vod_id:" + vod.id)
    print("    (uploadAudioToS3) meta.get(fulltitle)= " + downloaded_metadata.get('fulltitle'))
    print("    (uploadAudioToS3) s3fileKey= " + s3fileKey)
    # print(json.dumps(downloaded_metadata, default=lambda o: o.__dict__))
    s3 = boto3.client('s3')
    try:
        s3.upload_file(os.path.abspath(outfile_aux), env_varz.BUCKET_NAME, s3fileKey, ExtraArgs={ 'ContentType': 'audio/mpeg'})
        s3.put_object(Body=json.dumps(downloaded_metadata, default=lambda o: o.__dict__), ContentType="application/json; charset=utf-8", Bucket=env_varz.BUCKET_NAME, Key=s3metaKey)
        return s3fileKey
    except Exception as e:
        print("oops! failed mp3 or metadata upload " + str(e))
        return None
    

def updateVods_Round2Db(downloaded_metadata, vod_id, s3fileKey):
    def getTitle(meta):
        if meta.get('title'):
            title = meta.get('title')
        # elif meta.get('requested_downloads')[0].get('title'):
        #     title = meta.get('title')[0].get('title')
        elif meta.get('fulltitle'):
            title = meta.get('fulltitle')
        else: 
            title = vod_id
        return title

    title = getTitle(downloaded_metadata)
    duration = downloaded_metadata.get('duration')
    duration_string = downloaded_metadata.get('duration_string')
    view_count = downloaded_metadata.get('view_count')
    webpage_url = downloaded_metadata.get('webpage_url')
    thumbnail = downloaded_metadata.get('thumbnail')
    stream_epoch = int(downloaded_metadata.get('timestamp'))
    transcript_status = "audio2text_need"

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
                    S3Audio = %s
                WHERE Id = %s;
                """
            values = (title, duration, duration_string, view_count, webpage_url, thumbnail, transcript_status, stream_epoch, s3fileKey, vod_id)
            affected_count = cursor.execute(sql, values)
            print("    (updateVods_Round2Db) Updated " + vod_id + ". affected_counf= " + str(affected_count))
            connection.commit()
    except Exception as e:
        print(f"    (updateVods_Round2Db) Error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()


def updateErrorVod(vod: Vod, error_msg: str):
    print(f"Something failed with downloadTwtvVid2. Channel-Vod: {vod.channels_name_id}-{vod.id}. Error type: {error_msg}")
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
        print(f"Error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()

def cleanUpDownloads(downloaded_metadata):
    if env_varz.ENV == "local":
        print("Local Env. NOT cleaning up files")
        return
    extenstions = ['.mp3', '.mp4', '.opus']
    filename = downloaded_metadata.get('_filename') 
    last_dot_index = filename.rfind('.')
    for ex in extenstions:
        file_ = filename[:last_dot_index] + ex
        file_abs = os.path.abspath(file_)
        if os.path.exists(file_abs) and os.path.isfile(file_abs):
            os.remove(file_abs)
            print('Deleted: ' + str(file_abs))
    return 

# SELECT 
#     subquery.*,
#     Channels.CurrentRank
# FROM (
#     SELECT 
#         Vods.*,
#         ROW_NUMBER() OVER (PARTITION BY Vods.ChannelNameId ORDER BY TodoDate) as rn
#     FROM Vods 
# ) AS subquery
# JOIN Channels ON subquery.ChannelNameId = Channels.NameId 
# WHERE subquery.rn <= 2;



# SELECT 
#     subquery.*
# FROM (
#     SELECT 
#         Vods.*,
#         Channels.CurrentRank,
#         ROW_NUMBER() OVER (PARTITION BY Vods.ChannelNameId ORDER BY TodoDate) as rn
#     FROM Vods 
# 	JOIN Channels ON Vods.ChannelNameId = Channels.NameId
# ) AS subquery 
# WHERE subquery.rn <= 2
# ORDER BY CurrentRank