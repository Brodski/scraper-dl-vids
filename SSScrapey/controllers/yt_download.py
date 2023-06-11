from flask import Blueprint, current_app
import yt_dlp
import time

import boto3
import json
import datetime
from models.Metadata_Ytdl import Metadata_Ytdl
import controllers.yt_download as yt
# import models.Metadata_Yt as Metadata_Yt
import models.Metadata_Ytdl as Md_Ytdl
import controllers.whispererAi as whisperAI
import controllers.whispererAiFAST as whispererAiFAST
# from models.Metadata_Ytdl import Metadata_Ytdl
import yt_dlp
import subprocess
# from botocore.exceptions import NoCredentialsError, ClientError
from flask import jsonify, abort
import inspect

import os

import env_app as env_varz

CURRENT_DATE_YMD = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


test_bp = Blueprint('test', __name__)
vidUrl = 'https://www.twitch.tv/videos/1783465374' # pro leauge
vidUrl = 'https://www.twitch.tv/videos/1791750006' # lolgera
# vidUrl = 'https://www.twitch.tv/videos/1792255936' # sub only
vidUrl = 'https://www.twitch.tv/videos/1792342007' # live

def is_json_serializable(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False

def removeNonSerializable(meta):
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


# Download
#  https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L137-L312
# TODO???
# Turn this into (HTTP POST ---> Lambda)
def downloadTwtvVid(link:str, isDownload=True): 
    # https://www.twitch.tv/videos/28138895
    output_local_dir = "assets/audio"
    
    vidUrl = link if "youtube.com" in link.lower() else "https://www.twitch.tv" + link
        
    try:
        output_template = '{}/{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path, output_local_dir)
    except:
        output_template = '{}/{}/%(title)s-%(id)s.%(ext)s'.format(os.getcwd()+'/', output_local_dir)
    print ("000000000000                  00000000000000000")
    print ("000000000000 download twtvVid 00000000000000000")
    print ("000000000000                  00000000000000000")
    ydl_opts = {
        # format --> https://github.com/yt-dlp/yt-dlp#sorting-formats
        # 'format': 'worstaudio/Audio_Only/600/250/bestaudio/worstvideo/160p30',
        "outtmpl": output_template,
        "extractaudio": True,
        "format": "worst",
        "audioformat": "mp3",
        # "audioformat": "worst",
        # "listformats": True,
        # "audioformat": "mp3",
        "quiet": True,
        # "verbose": True,
        "parse_metadata" "requested_downloads.filepath:%(filepath):" 
        "overwrites": True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0', #https://trac.ffmpeg.org/wiki/Encode/MP3
        #     # 'preferredquality': '192', #https://trac.ffmpeg.org/wiki/Encode/MP3
        #                                 #https://github.com/ytdl-org/youtube-dl/blob/195f22f679330549882a8234e7234942893a4902/youtube_dl/postprocessor/ffmpeg.py#L302
        }],
    }

    start_time = time.time()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(vidUrl, download=isDownload) 
        except Exception as e:
            print ("Failed to extract vid info:" + str(e))
            return None
    print('--------TOP-----------x')
    print('  (dlTwtvVid) Download complete: time=' + str(time.time() - start_time))
    meta = removeNonSerializable(meta)
    filepath = meta.get('requested_downloads')[0].get('filepath')  #C:\Users\SHAAAZAM\scraper-dl-vids\assets\audio\Calculated-v5057810.mp3
    inFile = "file:" + filepath
    outFile =  "".join(inFile.split(".")[:-1]) + "-out.opus" 
    print("  (dlTwtvVid) getMeta vidUrl= " + vidUrl)
    print("  (dlTwtvVid) getMeta vid.output= " + output_template)
    print("  (dlTwtvVid) filepath= "+filepath)
    print("  (dlTwtvVid) inFile= "+inFile)
    print("  (dlTwtvVid) outFile= "+outFile)
    print("")

    # https://superuser.com/questions/1422460/codec-and-setting-for-lowest-bitrate-ffmpeg-output
    #  ffmpeg -i '.\Adc Academy - Informative Adc Stream - GrandMaster today？ [v1792628012].mp3' -c:a libopus -ac 1 -ar 16000 -b:a 33K -vbr constrained gera33k.opus
    # ffmpeg_command = [ 'ffmpeg', '-i', inFile, '-q:a', '0', '-map', 'a', inFile+'.mp3' ]
    # _execFFmpegCmd(ffmpeg_command)
    ffmpeg_command = [
        # 'ffmpeg', '-version'
        # 'ffmpeg', '-y', '-i', inFile, '-filter:a', 'atempo=1.5', outFile
        'ffmpeg', '-y', '-i',  inFile, '-c:a', 'libopus', '-ac', '1', '-ar', '16000', '-b:a', '10K', '-vbr', 'constrained', outFile
    ]
    # _execFFmpegCmd(ffmpeg_command)
    
    end_time = time.time() 
    time_diff = end_time - start_time
    
    print("     Download + FFMpeg cmd = ", str(time_diff))
    print('---------BOT----------x')
    # print(meta)
    return meta

# Queue up X vids from Y channels
# def createDownloadQueue(scrapped_channels_with_todos,*, chnLimit=10, vidDownloadLimit=10) -> List[str]:
#     queueOfLinks = []
#     chnCounter = 0
#     for channel in scrapped_channels_with_todos:
#         if chnCounter == chnLimit:
#             break
#         chnCounter = chnCounter + 1
#         vidCount = 0
#         for link in channel['todos']:
#             if vidCount == vidDownloadLimit:
#                 break
#             vidCount = vidCount + 1
#             queueOfLinks.append(link)
    
    
def _execFFmpegCmd(ffmpeg_command):
    try:
        # print("    (exec) starting subprocess!")
        print("    (exec) ffmpeg_command=" + " ".join(ffmpeg_command))
        # print("    (exec) ffmpeg_command=" + str(ffmpeg_command))
        stdoutput, stderr, returncode = yt_dlp.utils.Popen.run(ffmpeg_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        # print("    (exec) FFMPEG PIPE COMPLETE")
        # print("")
        # print(stdoutput)
        # print("")
        # print(stderr)
        # print("")
        # print(returncode)
        # print("")
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to run ffmpeg command:")
        print(e)
        return False

# Download X vids from Y channels. 
def bigBoyChannelDownloader(scrapped_channels_with_todos,*, chnLimit=10, vidDownloadLimit=10):
    print ("000000000000                         00000000000000000")
    print ("000000000000 bigBoyChannelDownloader 00000000000000000")
    print ("000000000000                         00000000000000000")
    for chn in scrapped_channels_with_todos:
        print("    (bigboy)" + chn.get('url'))
    metadata_Ytdl_list = []
    chnCounter = 0
    for channel in scrapped_channels_with_todos:
        if chnCounter == chnLimit:
            break
        chnCounter = chnCounter + 1
        print ("    (bigboy) ----> " + str(chnCounter) + " Channel: " + channel.get("url") + " ---> # links = " + str(len(channel.get("links"))))
        print ("    (bigboy) ----> " + str(channel))
        print ("    (bigboy) downloading channel_with_todos (via yt_dl) ................")
        vidCount = 0
        for link in channel['todos']:
            if vidCount == vidDownloadLimit:
                break
            vidCount = vidCount + 1
            print ("    (bigboy) ----> chn #" + str(chnCounter) + " vid #" + str(vidCount))
            print ("    (bigboy) ----> " + channel.get("url") + " @ " + link)
            metadata = downloadTwtvVid(link, True)

            metadata_Ytdl = Md_Ytdl.Metadata_Ytdl(channel['url'], channel['displayname'], channel['language'], channel['logo'], channel['twitchurl'], link, metadata) # Meta(lolgeranimo, /video/12345123, {... really big ... })
            metadata_Ytdl_list.append(metadata_Ytdl)
            print("    (bigboy) metadata_Ytdl=" + str(metadata_Ytdl))
            print("    (bigboy) completed: " + metadata_Ytdl.channel + " @ " + metadata_Ytdl.link)
        
        print()
        print()
        print("    (bigboy) metadata_Ytdl_list:")
        print("    (bigboy) " + str (metadata_Ytdl_list))
        print()
        print()
    return metadata_Ytdl_list

def uploadAudioToS3(yt_meta: Metadata_Ytdl, isDebug=False):
    print ("000000000000                 00000000000000000")
    print ("000000000000 uploadAudioToS3 00000000000000000")
    print ("000000000000                 00000000000000000")
    # caption_keybase = channels/vod-audio/lolgeranimo/2023-04-18/1747933567 
    # channels/vod-audio/<CHANNEL>/<TODAY-DATE>/<VID-ID/URL>.MP3 

    meta = yt_meta.metadata
    filepath = meta.get('requested_downloads')[0].get('filepath')
    vodTitle = meta.get('fulltitle')
    display_id = meta.get('display_id')
    ext = meta.get("requested_downloads")[0].get('ext')
    vod_filename = vodTitle + "-" + display_id + "." + ext

    # caption_keybase = channels/vod-audio/lolgeranimo/2023-04-18/1747933567 
    # caption_keybase = env_varz.S3_CAPTIONS_KEYBASE + yt_meta.channel + "/" + CURRENT_DATE_YMD + yt_meta.link.replace("/videos", "") 
    caption_keybase = env_varz.S3_CAPTIONS_KEYBASE + yt_meta.channel + "/" + yt_meta.link.replace("/videos/", "") 
    s3fileKey = caption_keybase + '/' + vod_filename
    s3metaKey = caption_keybase + "/metadata.json"
    print("")
    print("    " + str(yt_meta.metadata)[:100])
    print("    uploading: " +yt_meta.channel)
    print("    link: " + yt_meta.link)
    # print("    filepath:" + meta.get('requested_downloads')[0].get('filepath'))
    print("    file= " + filepath)
    print("    s3fileKey= " + s3fileKey)
    print("    metaKey= " + s3metaKey)
    print("")
    # if isDebug:
    #     print("IS DEBUG - DIDNT ACTUALLY UPDLOAD")
    #     return
    s3 = boto3.client('s3')
    try:
        # upload: channels/vod-audio/lck/2023-04-18/576354726/metadta.json
        # upload: channels/vod-audio/lck/2023-06-02/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.mp3
        print ("    UPLOADING MP3 !!!!!!!!!!!!!!!!! ")
        s3.upload_file(filepath, env_varz.BUCKET_NAME, s3fileKey)
        print ("    UPLOADING META !!!!!!!!!!!!!!!!! ")
        # print(json.dumps(yt_meta.__dict__))
        print ()
        print ()
        print ()
        print ()
        # print (json.dumps(yt_meta))
        # s3.put_object(Body=str(yt_meta.toJSON()), Bucket=env_varz.BUCKET_NAME, Key=s3metaKey)
        s3.put_object(Body=json.dumps(yt_meta.__dict__), Bucket=env_varz.BUCKET_NAME, Key=s3metaKey)
        return True
    except Exception as e:
        print("oops! " + str(e))
        return False




#############################################################
# NOT USED                                                  #
# ??????????
# Adds an json object to env_varz.S3_ALREADY_DL_KEYBASE 
# Adds to 'channels/scrapped/lolgeranimo.json'
# def updateScrapeHistory(metadata_json):
#     if metadata_json is None:
#         return
#     already_downloaded_json = getAlreadyDownloadedS3(metadata_json['uploader'])
#     s3 = boto3.client('s3')
#     s3.put_object(
#         Body=json.dumps(metadata_json),
#         Bucket=env_varz.BUCKET_NAME,
#         Key=env_varz.S3_ALREADY_DL_KEYBASE + metadata_json['uploader']
#     )
#     print( "done: \n")
#                                                             #
###############################################################


###############################################################
# NOT USED                                                    #
#
# TODO
# Get From s3, eg channels/scrapped/lolgeranimo.json
# returns some json
def getAlreadyDownloadedS3(channel):
    print ("xxxxxxxxxxxx                        xxxxxxxxxxxx")
    print ("xxxxxxxxxxxx getAlreadyDownloadedS3 xxxxxxxxxxxx")
    print ("xxxxxxxxxxxx                        xxxxxxxxxxxx")
  
    s3 = boto3.client('s3')
    
    objects = s3.list_objects_v2(Bucket=env_varz.BUCKET_NAME, Prefix=env_varz.S3_ALREADY_DL_KEYBASE)['Contents']
    print("     (getAlreadyDownloadedS3) looking for channel: "+ channel)
    # isFound = False
    # for obj in objects:
    #     print("---------------------")
    #     print(obj)
    #     print("key: " + str(obj['Key'].split(',')))
    #     if ( channel in obj['Key'].split(',')):
    #         return "True"
    
    try:
        responseGetObj = s3.get_object(
            Bucket = env_varz.BUCKET_NAME,
            Key = env_varz.S3_ALREADY_DL_KEYBASE + channel # ex) 'channels/scrapped/lolgeranimo.json'
        )
    except:
        print("    (getAlreadyDownloadedS3) found nothing!")
        return None
        
    
    binary_data = responseGetObj['Body'].read()

    json_string = binary_data.decode('utf-8')
    json_object = json.loads(json_string) # { "data":[ { "viewminutes":932768925, "streamedminutes":16245, ... } ] }
    print("    (getAlreadyDownloadedS3) GOT THIS------------")
    print(json_object)
    return json_object
#                                                           #
#############################################################


def getAlreadyDownloadedS3_TEST(channel):
    x = getAlreadyDownloadedS3(channel)
    if x:
        return x
    else: 
        abort(404, description="Username not found")

# Prob coulda make this method part of the "scrapped_channel" object
# Make sure we havent already DL the vid
def addTodoListS3(scrapped_channels):
    print ("000000000000                    00000000000000000")
    print ("000000000000 addTodoListS3 00000000000000000")
    print ("000000000000                    00000000000000000")
    print("    (addTodoS3) Making sure we havent already DL'd the vid")
    # todo_downloads_objlist = []
    cnt = 0
    for scrap_channel in scrapped_channels:
        print(str(cnt) + " (addTodoS3) TOP ---------")
        print(scrap_channel)
        cnt = cnt + 1
        already_downloaded = yt.getAlreadyDownloadedS3(scrap_channel['url'])
        print("     (addTodoS3) already_downloaded")
        print(already_downloaded)
        print() 
        # Probably a better way to write this :/
        # If the scrapped links doesnt exist in our already_downloaded list then add to todos
        todo_downloads = []
        for link in scrap_channel['links']:
            if already_downloaded is None:
                todo_downloads = scrap_channel['links']
                break
            if not link in already_downloaded:
                todo_downloads.append(link)
        scrap_channel['todos'] = todo_downloads # B/c reference
        # todo_downloads_objlist.append({ 
        #     "displayname": channel['displayname'],
        #     "todos": todo_downloads
        # })
        print(str(cnt) + " (addTodoS3) BOT ---------")
    return scrapped_channels
    # return todo_downloads_objlist
    
    # key = s3_key_ranking + ".json" # channels/rankings/raw/2023-15/2.json
    # print("saving json file to: " + key)
    # s3.put_object(
    #     Body=json.dumps(json_data),
    #     Bucket=env_varz.BUCKET_NAME,
    #     Key= env_varz.S3_ALREADY_DL_KEYBASE + "lolgeranimo/" + date
    # )

