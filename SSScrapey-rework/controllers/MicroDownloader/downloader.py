
import json
import subprocess
import time
from models.AudioResponse import AudioResponse
from models.VodS3Response import VodS3Response
from models.Metadata_Ytdl import Metadata_Ytdl
from models.ScrappedChannel import ScrappedChannel
# from models.Vod import Vod
from controllers.MicroDownloader.Vod import Vod
from typing import List
from datetime import datetime

from dotenv import load_dotenv
from flask import Blueprint, current_app
from flask import jsonify, abort

import os
import MySQLdb
import yt_dlp


# load_dotenv()
import env_file as env_varz

def getTodoFromDatabase(isDebug=False) -> List[Vod]:
    resultsArr = []
    connection = MySQLdb.connect(
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        db      = env_varz.DATABASE,
        autocommit  = True,
        ssl_mode    = "VERIFY_IDENTITY",
        ssl         = { "ca": "C:/Users/BrodskiTheGreat/Documents/HeidiSQL/cacert-2023-08-22.pem" } # See https://planetscale.com/docs/concepts/secure-connections#ca-root-configuration to determine the path to your operating systems certificate file.
    )
    try:
        with connection.cursor() as cursor:
            sql = """   SELECT Vods.*, Channels.CurrentRank AS ChanCurrentRank
                        FROM Vods
                        JOIN Channels ON Vods.ChannelNameId = Channels.NameId
                        WHERE Vods.TranscriptStatus = 'todo'
                        ORDER BY Channels.CurrentRank ASC, Vods.Priority ASC
                        LIMIT 1"""
            # sql = "SELECT Vods.* FROM Vods JOIN Channels ON Vods.ChannelNameId = Channels.NameId WHERE Vods.TranscriptStatus = 'todo' ORDER BY Channels.CurrentRank ASC, Vods.Priority ASC LIMIT 4";
            cursor.execute(sql)

            results = cursor.fetchall()
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        connection.close()
    for vod_ in results:
        print (vod_)
        # Tuple unpacking
        Id, ChannelNameId, Title, Duration, DurationString, ViewerCount, WebpageUrl, UploadDate, Timestamp, TranscriptStatus, Priority, ChanCurrentRank = vod_
        vod = Vod(Id, ChannelNameId, TranscriptStatus, Priority, ChanCurrentRank)
        resultsArr.append(vod)

    return resultsArr



def downloadVod(vod: Vod, *, isDebug):
    downloaded_metadata = downloadTwtvVid(vod, True)
    downloaded_metadata = removeNonSerializable(downloaded_metadata)
    meta, outfile = convertVideoToSmallAudio(downloaded_metadata)
    # TODO 
    # TODO this object
    # metadata_dl_file = Metadata_dl_file(vod.channels_name_id, "assname", )

    # metadata_Ytdl = Metadata_Ytdl(channel['name_id'], channel['displayname'], channel['language'], channel['logo'], channel['twitchurl'], link, outFile, metadata) # Meta(lolgeranimo, /video/12345123, {... really big ... })
    # metadata_Ytdl_list.append(metadata_Ytdl)

    # TODO
    # upload to S3 
    # updated SQL database as 'completed'
    return "metadata_Ytdl_list in prog"


def downloadTwtvVid(vod: Vod, isDownload=True): 
    if vod == None or vod.id == None:
        print("ERROR >.< no vod")
        return
    
    output_local_dir = "assets/audio"
    vidUrl = "https://www.twitch.tv/videos/" + vod.id
    start_time = time.time()

    print("  (dlTwtvVid) doing new downloader extract/download stuff...")
    print("  (dlTwtvVid) getMeta vidUrl= " + vidUrl)
    try:
        output_template = '{}/{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path, output_local_dir)
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
            print ("Failed to extract vid!!: " + vidUrl + " : " + str(e))
            return None, None

    print('  (dlTwtvVid) Download complete: time=' + str(time.time() - start_time))
    if meta == None:
        print("  (dlTwtvVid) Something failed with downloadVod")
        return -1
    return meta
    


def convertVideoToSmallAudio(meta):
    start_time = time.time()
    def getTitle(meta):
        if meta.get('title'):
            title = meta.get('title')
        elif meta.get('requested_downloads')[0].get('title'):
            title = meta.get('title')[0].get('title')
        else: 
            title = meta.get('fulltitle') 
        return title

    filepath = meta.get('requested_downloads')[0].get('filepath')  #C:\Users\SHAAAZAM\scraper-dl-vids\assets\audio\Calculated-v5057810.mp3
    title = getTitle(meta)
    inFile = "file:" + filepath
    if env_varz.WHSP_EXEC_FFMPEG == "True":
        outFile =  "".join(inFile.split(".")[:-1]) + ".opus" #opus b/c of the ffmpeg cmd below
    else:
        outFile = inFile
    
    print("  (dlTwtvVid) filepath= "+filepath)
    print("  (dlTwtvVid) title= "+title)
    print("  (dlTwtvVid) inFile= "+inFile)
    print("  (dlTwtvVid) outFile= "+outFile)

    # Debugging commands:
    # ffmpeg -i '.\Adc Academy - Informative Adc Stream - GrandMaster today？ [v1792628012].mp3' -c:a libopus -ac 1 -ar 16000 -b:a 33K -vbr constrained gera33k.opus
    # ffmpeg_command = [ 'ffmpeg', '-i', inFile, '-q:a', '0', '-map', 'a', inFile+'.mp3' ]
    # ffmpeg_command = [        
    #     'ffmpeg', '-version'
    #     'ffmpeg', '-y', '-i', inFile, '-filter:a', 'atempo=1.5', outFile
    # ]

    # https://superuser.com/questions/1422460/codec-and-setting-for-lowest-bitrate-ffmpeg-output
    ffmpeg_command = [
        'ffmpeg', '-y', '-i',  inFile, '-c:a', 'libopus', '-ac', '1', '-ar', '16000', '-b:a', '10K', '-vbr', 'constrained', outFile
    ]
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
            print("Something wrong with :" + str(key))
            to_delete.append(key)
    for d in to_delete: # FFmpegFixupM3u8PP is not serializable, adding this semi annoying logic so i never need to look at this agian
        del meta[d]
    return meta
