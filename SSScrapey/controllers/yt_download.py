from flask import Blueprint, current_app
import yt_dlp
import time

import boto3
import json
import datetime
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

import os

CURRENT_DATE_YMD = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
BUCKET_NAME = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket'
directory_name = 'mydirectory' # this directory legit exists in this bucket ^
directory_name_real = "channels/ranking/raw" 
S3_ALREADY_DL_KEYBASE = 'channels/scrapped/'
S3_CAPTIONS_KEYBASE = 'channels/captions/'
# S3_ALREADY_DL_KEY = 'channels/scrapped/lolgeranimo/2023-04-01.json'

test_bp = Blueprint('test', __name__)
vidUrl = 'https://www.twitch.tv/videos/1783465374' # pro leauge
vidUrl = 'https://www.twitch.tv/videos/1791750006' # lolgera
# vidUrl = 'https://www.twitch.tv/videos/1792255936' # sub only
vidUrl = 'https://www.twitch.tv/videos/1792342007' # live

# Download
#  https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L137-L312
# TODO???
# Turn this into (HTTP POST ---> Lambda)
def downloadTwtvVid(link:str, isDownload=True): 
    # https://www.twitch.tv/videos/28138895
    output_local_dir = "assets/raw"
    
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
        'format': 'Audio_Only/600/250/bestaudio/worstvideo/160p30',
        "outtmpl": output_template,
        "quiet": True,
        # "verbose": True,
        # "concurrent_fragment_downloads": 8
        'keepvideo': True,
        "addmetadata": True,
        "addchapters": True,
        "parse_metadata" "requested_downloads.filepath:%(filepath):" 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        },],
        "overwrites": True,
        # 'exec_cmd': '-filter:a "atempo=1.5"' #doesnt mfo work
    }

    start_time = time.time()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(vidUrl, download=isDownload) 
        except Exception as e:
            print ("Failed to extract vid info:" + str(e))
            return None
    print('-------------------x')
    print('Download complete: time=' + str(time.time() - start_time))
    filepath = meta.get('requested_downloads')[0].get('filepath')  #C:\Users\SHAAAZAM\scraper-dl-vids\assets\raw\Calculated-v5057810.mp3
    inFile = "file:" + filepath
    extension = inFile.split(".")[-1]
    outFileFAST =  "".join(inFile.split(".")[:-1]) + "-fast." + extension
    print("getMeta vidUrl=" + vidUrl)
    print("getMeta vid.output= " + output_template)
    print("filepath="+filepath)
    print("inFile="+inFile)
    print("outFileFAST="+outFileFAST)


    # try:
    #     print("starting subprocess!")
    #     ffmpeg_command = [
    #         # 'ffmpeg', '-version'
    #         'ffmpeg', '-y', '-i', inFile, '-filter:a', 'atempo=1.5', outFile
    #     ]
    #     print("ffmpeg_command=" + "".join(ffmpeg_command))
    #     stdoutput, stderr, returncode = yt_dlp.utils.Popen.run(ffmpeg_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    #     print("FFMPEG PIPE COMPLETE")
    #     print(stdoutput)
    #     print(stderr)
    #     print(returncode)
    #     print()
    # except subprocess.CalledProcessError as e:
    #     print("Failed to run ffmpeg command:")
    #     print(e)
    end_time = time.time() 
    time_diff = end_time - start_time
    
    print('--------------------x')
    print("Download + FFMpeg speedup = ", str(time_diff))
    print("***********************************")
    # print(meta)
    return meta
    try:
        x = json.dumps(meta)
        return x
    except:
        print("except done :(")
        print("except done :(")
        print("except done :(")
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
    
    
# def bigBoyChannelDownloader2(queueOfLinks):
#     for link in queueOfLinks:

# TODO env debugg variables
# Download X vids from Y channels
def bigBoyChannelDownloader(scrapped_channels_with_todos,*, chnLimit=10, vidDownloadLimit=10):
    metadata_Ytdl_list = []
    chnCounter = 0
    for channel in scrapped_channels_with_todos:
        if chnCounter == chnLimit:
            break
        chnCounter = chnCounter + 1
        print ("downloading this channel_with_todos......................")
        print (channel)
        vidCount = 0
        for link in channel['todos']:
            if vidCount == vidDownloadLimit:
                break
            vidCount = vidCount + 1
            # Download the vid
            # MAKE A LAMBDA??
            metadata = downloadTwtvVid(link, True)
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            metadata_Ytdl = Md_Ytdl.Metadata_Ytdl(channel['url'], link, metadata) # Meta(lolgeranimo, /video/12345123, {... really big ... })
            metadata_Ytdl_list.append(metadata_Ytdl)
            print("metadata_Ytdl=" + str(metadata_Ytdl))
            # try:
            #      print("metadata_Ytdl="+ str(json.dumps(metadata_Ytdl.__dict__)))
            # except:
            #     pass # print("failed to dump: " + metadata_Ytdl.username + " @ " + metadata_Ytdl.link + " - Fail" )
            print("completed: " + metadata_Ytdl.username + " @ " + metadata_Ytdl.link)
        
        print()
        print()
        print("metadata_Ytdl_list:")
        print(metadata_Ytdl_list)
        print()
        print()
    return metadata_Ytdl_list

# Nope
#
# def transcribefileWhisperAi(metadata_Ytdl):
#     output_local_dir = "assets/raw"
#     output_local_dir = "./assets/raw"
#     print("#############                         #############")
#     print("############# transcribefileWhisperAi #############")
#     print("#############                         #############")
#     isPass = False

#     for requested in metadata_Ytdl.metadata.get('requested_downloads', []):
#         print(requested.get('format_id', {}))
#         if requested.get('format_id') == "Audio_Only": # TODO othe audio_ids like youtube's, ect
#             __finaldir = requested.get('__finaldir') # "C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids"
#             filepath = requested.get("filepath")     # "C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids\\Bootcamp to Challenger \uff5c-v1747933567.f_Audio_Only.mp3"
#             filename = filepath.replace(__finaldir, "")
#             filename = filename[1:] if (filename[0] == "/" or filename[0] == "\\") else filename # filename = "Bootcamp to Challenger \uff5c-v1747933567.f_Audio_Only.mp3"

#             # ffmpeg convertion to audio doesnt change extension -.-
#             filename = (filename[:-4] + ".mp3") if filename[-4:] == ".mp4" else filename # NOTE position of ":" is diff

#             output_full_dir = "{}/{}/{}".format(current_app.root_path, output_local_dir, filename)
#             print ("---------------> ADDING " + filename)
#             print ("@  " + output_full_dir)
#             print(filename)
#             # NEED TO UPLOAD FILE FROM DIRECTORY TO BUCKET
#             isPass = whispererAiFAST.mp3FastTranscribe(filename)
        
#     return isPass

def uploadAudioToS3(yt_meta):
    s3 = boto3.client('s3')
    print("************** uploading file to s3() ****************")
    print("************** uploading file to s3() ****************")
    print("************** uploading file to s3() ****************")

    keybase = S3_CAPTIONS_KEYBASE + yt_meta.username + "/" + CURRENT_DATE_YMD + yt_meta.link.replace("/videos", "") 
    # ^ channels/captions/lolgeranimo/2023-04-18/1747933567
    metaKey = keybase + "/metadata.json"
    print("GETTINGGGGGGGGGGGGGG")
    print(yt_meta)
    print(yt_meta.username)
    print(yt_meta.link)
    # print(yt_meta.metadata)
    print("??")
    print(str(yt_meta.metadata))
    # print(yt_meta.metadata)
    meta = yt_meta.metadata
    print(meta)
    # print(meta.get('requested_downloads'))
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    # print(meta.get('requested_downloads')[0])
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print(meta.get('requested_downloads')[0].get('filepath'))

    file = meta.get('requested_downloads')[0].get('filepath')
    s3fileKey =  keybase + '/' + file
    print("")
    print("file=" + file)
    print("s3fileKey=" + s3fileKey)
    print("metaKey=" + metaKey)
    print("")
    # try:
    #     s3.upload_file(file, BUCKET_NAME, s3fileKey)
    #     print ("UPLOADED !!!!!!!!!!!!!!!!! ")
    #     if file == filesToSave[-1]:
    #         s3.put_object(
    #             Body=json.dumps(metadata),
    #             Bucket=BUCKET_NAME,
    #             Key= metaKey  # channels/test/raw/2023-15/2.json
    #         )
    # except Exception as e:
    #     print("oops! " + str(e))
    #     return False


    # # Get absolute file path of downloaded audio
    # for requested in metadata.get('requested_downloads', []):
    #     print(requested.get('format_id', {}))
    #     if requested.get('format_id') == "Audio_Only":
    #         __finaldir = requested.get('__finaldir') # "C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids"
    #         filepath = requested.get("filepath")     # "C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids\\Bootcamp to Challenger \uff5c-v1747933567.f_Audio_Only.mp3"
    #         filename = filepath.replace(__finaldir, "")
    #         filename = filename[1:] if (filename[0] == "/" or filename[0] == "\\") else filename # filename = "Bootcamp to Challenger \uff5c-v1747933567.f_Audio_Only.mp3"
    #         print ("filename[-4:]=" + filename[-4:])
    #         filename = (filename[:-4] + ".mp3") if filename[-4:] == ".mp4" else filename # NOTE position of ":" is diff
    #         if filename:
    #             print ("---------------> ADDING to filesToSave " + filename)
    #             filesToSave.append(filename)
        

#############################################################
# NOT USED                                                  #
# ??????????
# Adds an json object to S3_ALREADY_DL_KEYBASE 
# Adds to 'channels/scrapped/lolgeranimo.json'
def updateScrapeHistory(metadata_json):
    if metadata_json is None:
        return
    already_downloaded_json = getAlreadyDownloadedS3(metadata_json['uploader'])
    s3 = boto3.client('s3')
    s3.put_object(
        Body=json.dumps(metadata_json),
        Bucket=BUCKET_NAME,
        Key=S3_ALREADY_DL_KEYBASE + metadata_json['uploader']
    )
    print( "done: \n")
#                                                             #
###############################################################


#############################################################
# NOT USED                                                  #
#
# TODO
# Get From s3, eg channels/scrapped/lolgeranimo.json
# returns some json
def getAlreadyDownloadedS3(username):
    s3 = boto3.client('s3')
    
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_ALREADY_DL_KEYBASE)['Contents']
    print("getAlreadyDownloadedS3() = = = = = = = =")
    print("looking for username: "+ username)
    # isFound = False
    # for obj in objects:
    #     print("---------------------")
    #     print(obj)
    #     print("key: " + str(obj['Key'].split(',')))
    #     if ( username in obj['Key'].split(',')):
    #         return "True"
    
    try:
        responseGetObj = s3.get_object(
            Bucket = BUCKET_NAME,
            Key = S3_ALREADY_DL_KEYBASE + username # ex) 'channels/scrapped/lolgeranimo.json'
        )
    except:
        return None
        
    
    binary_data = responseGetObj['Body'].read()

    json_string = binary_data.decode('utf-8')
    json_object = json.loads(json_string) # { "data":[ { "viewminutes":932768925, "streamedminutes":16245, ... } ] }
    print("getAlreadyDownloadedS3() GOT THIS------------")
    print(json_object)
    return json_object
#                                                           #
#############################################################


def getAlreadyDownloadedS3_TEST(username):
    x = getAlreadyDownloadedS3(username)
    if x:
        return x
    else: 
        abort(404, description="Username not found")

# Make sure we havent already DL the vid
def addTodoDownloads(scrapped_channels):
    print("addTodoDownloads - start")
    print("Making sure we havent already DL the vid")
    # todo_downloads_objlist = []
    for todo in scrapped_channels:
        print("000000000000000000000000000000000000000000000000")
        print(todo)
        already_downloaded = yt.getAlreadyDownloadedS3(todo['url'])
        print("already_downloaded")
        print(already_downloaded)
        print() 
        # Probably a better way to write this :/
        # If the scrapped links doesnt exist in our already_downloaded list then add to todos
        todo_downloads = []
        for link in todo['links']:
            if already_downloaded is None:
                todo_downloads = todo['links']
                break
            if not link in already_downloaded:
                todo_downloads.append(link)
        todo['todos'] = todo_downloads
        # todo_downloads_objlist.append({ 
        #     "displayname": channel['displayname'],
        #     "todos": todo_downloads
        # })
    return scrapped_channels
    # return todo_downloads_objlist
    
    # key = s3_key_ranking + ".json" # channels/rankings/raw/2023-15/2.json
    # print("saving json file to: " + key)
    # s3.put_object(
    #     Body=json.dumps(json_data),
    #     Bucket=BUCKET_NAME,
    #     Key= S3_ALREADY_DL_KEYBASE + "lolgeranimo/" + date
    # )

