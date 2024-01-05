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


# load_dotenv()
import env_file as env_varz

def getConnection():
    connection = MySQLdb.connect(
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        db      = env_varz.DATABASE,
        autocommit  = False,
        ssl_mode    = "VERIFY_IDENTITY",
        ssl         = { "ca": env_varz.SSL_FILE } # See https://planetscale.com/docs/concepts/secure-connections#ca-root-configuration to determine the path to your operating systems certificate file.
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
            # sql = """   SELECT Vods.*, Channels.CurrentRank AS ChanCurrentRank
            #             FROM Vods
            #             JOIN Channels ON Vods.ChannelNameId = Channels.NameId
            #             WHERE Vods.TranscriptStatus = 'todo'
            #             # ORDER BY Channels.CurrentRank ASC, Vods.TodoDate ASC, Vods.Priority ASC
            #             ORDER BY Vods.TodoDate ASC, Channels.CurrentRank ASC, Vods.Priority ASC
            #             LIMIT 100
            #             """
            cursor.execute(sql)
            results = cursor.fetchall()
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        connection.close()
    print("Vod candidates:")
    for vod_ in results:
        # Tuple unpacking
        Id, ChannelNameId, Title, Duration, DurationString, ViewCount, WebpageUrl, UploadDate, TranscriptStatus, Priority, Thumbnail, TodoDate, S3Audio, ChanCurrentRank, rownum, *others = vod_
        vod = Vod(id=Id, channels_name_id=ChannelNameId, transcript_status=TranscriptStatus, priority=Priority, channel_current_rank=ChanCurrentRank, todo_date=TodoDate)
        vod.print()
        resultsArr.append(vod)

    highest_priority_vod = None
    #Recall, results arr is sorted by priority via smart sql query
    for vod in resultsArr:
        vod.print()
        if vod.transcript_status == "todo":
            highest_priority_vod = vod
            break
    print("!!! highest_priority_vod: !!!")
    if highest_priority_vod:
        highest_priority_vod.print()
    if isDebug:
        highest_priority_vod = Vod(id="40792901", channels_name_id="nmplol", transcript="todo", priority=-1, channel_current_rank="-1") # (Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
        # vod = Vod(id="1964894986", channels_name_id="jd_onlymusic", transcript="todo", priority=0, channel_current_rank="-1") # (Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
        print("(debug) highest_priority_vod is this vod:")
        highest_priority_vod.print()
    return highest_priority_vod

def getNeededVod_OLD(vods_list: List[Vod]):    
    maxVodz = 2
    print("[][][][][][][][][][][][][][][][][][][][]")
    vods_dict_temp = {}
    vods_dict = {}
    for vod in vods_list:
        vods_dict_temp.setdefault(vod.channels_name_id, []).append(vod)
    for key in vods_dict_temp:
        print(f"{key}: {vods_dict_temp[key]}")
        for x in vods_dict_temp[key]:
            x.print()
        filtered_objects = [obj for obj in vods_dict_temp[key][:maxVodz] if obj.transcript_status == 'todo']
        if filtered_objects:
            vods_dict[key] = filtered_objects

    keyHighestPrioChan = list(vods_dict.keys())[0]
    vod: Vod = vods_dict[keyHighestPrioChan][0]
    print("NEXT VOD IN THEORY")
    vod.print()
    return vod

def lockVodDb(vod: Vod, isDebug=False):
    print("LOCKING VOD DB: " + str(vod.id))
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
            print(f"DB. Set {vod.id} to 'downloading', affected_count: : {affected_count}")
        connection.commit()
        return True
    except Exception as e:
        print(f"Error occurred: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


# 'API'  https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L137-L312
def downloadTwtvVid2(vod: Vod, isDownload=True): 
    if vod == None or vod.id == None:
        print("ERROR no vod")
        return

    output_local_dir = "assets/audio"
    vidUrl = "https://www.twitch.tv/videos/" + vod.id
    start_time = time.time()


    main_script_path = sys.argv[0]
    absolute_path = os.path.realpath(main_script_path)
    app_root = os.path.dirname(absolute_path)

    print("  (dlTwtvVid) vidUrl= " + vidUrl)
    print("  (dlTwtvVid) app_root= " + str(app_root))
    try:
        output_template = '{}/{}/%(title)s-%(id)s.%(ext)s'.format(app_root, output_local_dir)
    except:
        output_template = '{}/{}/%(title)s-%(id)s.%(ext)s'.format(os.getcwd()+'/', output_local_dir)

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
        # "audioformat": "mp3",
        "quiet": True,
        # "verbose": True,
        "noprogress": True if env_varz.ENV != "local" else False,
        "parse_metadata" "requested_downloads.filepath:%(filepath):"  # my custom  metadata field
        "overwrites": True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',        # https://trac.ffmpeg.org/wiki/Encode/MP3
        #     # 'preferredquality': '192',  # https://github.com/ytdl-org/youtube-dl/blob/195f22f679330549882a8234e7234942893a4902/youtube_dl/postprocessor/ffmpeg.py#L302
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
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
    return meta
    


def convertVideoToSmallAudio(meta):
    start_time = time.time()
    filepath = meta.get('requested_downloads')[0].get('filepath')  #C:\Users\SHAAAZAM\scraper-dl-vids\assets\audio\Calculated-v5057810.mp3
    inFile = "file:" + filepath
    if env_varz.WHSP_EXEC_FFMPEG == "True":
        last_dot_index = inFile.rfind('.')
        outFile = inFile[:last_dot_index] + ".opus"
        # outFile =  "".join(inFile.split(".")[:-1]) + ".opus" #opus b/c of the ffmpeg cmd below
    else:
        outFile = inFile
    
    print("  (dlTwtvVid) filepath= "+filepath)
    print("  (dlTwtvVid) inFile= "+inFile)
    print("  (dlTwtvVid) outFile= "+outFile)

    # Debugging commands:
    # ffmpeg -i '.\Adc Academy - Informative Adc Stream - GrandMaster today？ [v1792628012].mp3' -c:a libopus -ac 1 -ar 16000 -b:a 33K -vbr constrained gera33k.opus
    # ffmpeg_command = [ 'ffmpeg', '-i', inFile, '-q:a', '0', '-map', 'a', inFile+'.mp3' ]
    # ffmpeg_command = [ 'ffmpeg', '-version' ]
    # ffmpeg_command = [ 'ffmpeg', '-y', '-i', inFile, '-filter:a', 'atempo=1.5', outFile ]

    # https://superuser.com/questions/1422460/codec-and-setting-for-lowest-bitrate-ffmpeg-output
    ffmpeg_command = [ 'ffmpeg', '-y', '-i',  inFile, '-c:a', 'libopus', '-ac', '1', '-ar', '16000', '-b:a', '10K', '-vbr', 'constrained', outFile ]
    if env_varz.WHSP_EXEC_FFMPEG == "True":
        _execFFmpegCmd(ffmpeg_command)

    time_diff = time.time() - start_time    
    print("     FFMpeg cmd time = ", str(time_diff))
    print('---------BOT----------x')
    return meta, outFile
    
def _execFFmpegCmd(ffmpeg_command):
    try:
        # print("    (exec) FFMPEG: starting subprocess!")
        print("    (exec) ffmpeg_command=" + " ".join(ffmpeg_command))
        stdoutput, stderr, returncode = yt_dlp.utils.Popen.run(ffmpeg_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        # print("    (exec) FFMPEG:  PIPE COMPLETE")
        # print(stdoutput)
        # print(stderr)
        # print(returncode)
        return True
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

    ext = downloaded_metadata.get("requested_downloads")[0].get('ext')
    caption_keybase = env_varz.S3_CAPTIONS_KEYBASE + vod.channels_name_id + "/" + vod.id
    vod_title = os.path.basename(outfile)
    vod_encode = urllib.parse.quote(vod_title)
    s3fileKey = caption_keybase + "/" + vod_encode
    s3metaKey = caption_keybase + "/metadata.json"
    print("")
    print("    (uploadAudioToS3) uploading channel: " + vod.channels_name_id)
    print("    (uploadAudioToS3)  vod_id:" + vod.id)
    print("    (uploadAudioToS3) meta.get(fulltitle)= " + downloaded_metadata.get('fulltitle'))
    print("    (uploadAudioToS3) ext = " + ext)
    print("    (uploadAudioToS3) s3fileKey= " + s3fileKey)
    print("    (uploadAudioToS3) metaKey= " + s3metaKey)
    print ("    " + outfile[5:])
    print("")
    # print(json.dumps(downloaded_metadata, default=lambda o: o.__dict__))
    s3 = boto3.client('s3')
    try:
        s3.upload_file(os.path.abspath(outfile[5:]), env_varz.BUCKET_NAME, s3fileKey, ExtraArgs={ 'ContentType': 'audio/mpeg'})
        s3.put_object(Body=json.dumps(downloaded_metadata, default=lambda o: o.__dict__), ContentType="application/json; charset=utf-8", Bucket=env_varz.BUCKET_NAME, Key=s3metaKey)
        return s3fileKey
    except Exception as e:
        print("oops! failed mp3 or metadata upload " + str(e))
        return None
    

def updateVods_Round2Db(downloaded_metadata, vod_id, s3fileKey):
    def getTitle(meta):
        if meta.get('title'):
            title = meta.get('title')
        elif meta.get('requested_downloads')[0].get('title'):
            title = meta.get('title')[0].get('title')
        else: 
            title = meta.get('fulltitle') 
        return title

    title = getTitle(downloaded_metadata)
    duration = downloaded_metadata.get('duration')
    duration_string = downloaded_metadata.get('duration_string')
    view_count = downloaded_metadata.get('view_count')
    webpage_url = downloaded_metadata.get('webpage_url')
    timestamp_twtw_uploaded = downloaded_metadata.get('timestamp') # upload_date
    thumbnail = downloaded_metadata.get('thumbnail')
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
                    UploadDate = FROM_UNIXTIME(%s),
                    Thumbnail = %s,
                    TranscriptStatus = %s,
                    S3Audio = %s
                WHERE Id = %s;
                """
            values = (title, duration, duration_string, view_count, webpage_url, timestamp_twtw_uploaded, thumbnail, transcript_status, s3fileKey, vod_id)
            affected_count = cursor.execute(sql, values)
            print("Updated these many" + str(affected_count))
        connection.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
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
    x = downloaded_metadata.get("requested_downloads")

    filename_opus = None
    filename = x[0].get('filepath') 
    file_abs = os.path.abspath(filename)
    os.remove(file_abs)       
    if filename.endswith('.mp3'):
        filename_opus = filename[:-4] + ".opus"
        file_abs_opus = os.path.abspath(filename_opus) if filename_opus else None
        print("file_abs_opus")
        print(file_abs_opus)
        os.remove(file_abs_opus)
    print('Deleted: ' + str(file_abs))
    print('Deleted: ' + str(file_abs_opus))
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