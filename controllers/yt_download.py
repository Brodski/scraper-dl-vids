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
def downloadTwtvVid(link, isDownload=True): 
    # https://www.twitch.tv/videos/28138895
    vidUrl = "https://www.twitch.tv" + link
    output_local_dir = "assets/raw"
    output_template = '{}/{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path, output_local_dir)
    print ("000000000000                  00000000000000000")
    print ("000000000000 download twtvVid 00000000000000000")
    print ("000000000000                  00000000000000000")
    ydl_opts = {
        # format --> https://github.com/yt-dlp/yt-dlp#sorting-formats
        # 'format': 'sb0,sb1,sb2,Audio_Only/600/250/worstvideo/bestaudio/160p30',
        'format': 'Audio_Only/600/250/bestaudio/worstvideo/160p30',
        # 'outtmpl': '{}/%(title)s-%(id)s.f%(format_id)s.%(ext)s'.format(current_app.root_path),
        # "outtmpl": "%(title)s-%(id)s.f_%(format_id)s.%(ext)s",
        "outtmpl": output_template,
        "verbose": True,
        # "concurrent_fragment_downloads": 8
        'keepvideo': True,
        "addmetadata": True,
        "addchapters": True,
        # "parse_metadata" "requested_downloads.filepath:%(filepath):" 
        # 'nopostoverwrites': True,
        #### !! 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            # 'options': ['-filter:a', 'atempo=1.5']
        },
            # ChatGPT4 hallucinating bullshit postprocessors. FFmpegAudioConvertor does not exist. 
            # ChatGPT3 made up FFmpegAudioSpeed too -.-
            # {
            #     'key': 'FFmpegAudioConvertor',
            #     'options': '-filter:a "atempo=1.5"',
            # }
        ],
        "overwrites": True,
        # "nopostoverwrites": False, # hacked yt-dlp.FFmpegExtractAudioPP
        # 'exec_cmd': 'after_video: --ffmpeg-exec.bat'
        'exec_cmd': '-filter:a "atempo=1.5"'
    }
    print ("getMeta vidUrl=" + vidUrl)
    print ("getMeta vidUrl=" + vidUrl)
    print ("getMeta vidUrl=" + vidUrl)
    print ("getMeta vidUrl=" + vidUrl)
    print ("getMeta vid.output= " + output_template)
    # return "gg"
    # YES https://www.twitch.tv/videos/1778309747?filter=archives&sort=time
    # NO  https://www.twitch.tv/lolgeranimo/videos/1778309747

    start_time = time.time()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(vidUrl, download=isDownload) 
        except Exception as e:
            print ("Failed to extract vid info:" + str(e))
            return None
    print('-------------------x')
    print('Download complete: time=' + str(time.time() - start_time))
    print()
    print()
    print(meta.get('requested_downloads')[0].get('filepath'))
    inFile = "file:" + meta.get('requested_downloads')[0].get('filepath')
    extension = inFile.split(".")[-1]
    outFile =  "".join(inFile.split(".")[:-1]) + "-fast." + extension
    print("inFile="+inFile)
    print("outFile="+outFile)

    ffmpeg_command = [
        'ffmpeg', '-i', inFile, '-filter:a', 'atempo=1.5', outFile
    ]
    # ffmpeg -y -loglevel "repeat+info" -i "file:C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\assets\raw\Calculated-v5057810.mp4" -map 0 -dn -ignore_unknown -c copy -f mp4 "-bsf:a" aac_adtstoasc -movflags "+faststart" "file:C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\assets\raw\Calculated-v5057810.temp.mp4"    
    # ffmpeg -y -loglevel "repeat+info" -i "file:C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\assets\raw\Calculated-v5057810.mp3" -filter:a "atempo=1.5" "file:C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\assets\raw\Calculated-v5057810.mp3"
    # ffmpeg -i file:C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\assets\raw\Calculated-v5057810.mp3 -filter:a "atempo=1.5" file:C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\assets\raw\Calculated-v5057810.mp3
 

    print("starting subprocess!")
    try:
        # stdoutput, stderr, returncode = yt_dlp.utils.Popen.run("where ffmpeg", text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        # print("BAM!")
        # print("BAM!")
        # print(stdoutput)
        # print(stderr)
        # print(returncode)    
        ffmpeg_command = [
            # 'ffmpeg', '-version'
            'ffmpeg', '-y', '-i', inFile, '-filter:a', 'atempo=1.5', outFile
        ]
        print("gogo")
        print(ffmpeg_command)
        stdoutput, stderr, returncode = yt_dlp.utils.Popen.run(ffmpeg_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(stdoutput)
        print(stderr)
        print(returncode)    
        # subprocess.call(ffmpeg_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        # subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print("Done subprocess!!!!!!!!!!!!!!!!!!!")
    except subprocess.CalledProcessError as e:
        print("Failed to run ffmpeg command:")
        print(e)
    end_time = time.time() 
    time_diff = end_time - start_time
    
    print('--------------------x')
    # print(meta)
    # print('upload date : %s' %(meta['upload_date']))
    # print( 'uploader    : %s' %(meta['uploader']))
    # print( 'views       : %d' %(meta['view_count']))
    # print( 'likes       : %s' %(meta.get('like_count', 'nope :o')))
    # print( 'dislikes    : %s' %(meta.get('dislike_count', 'no dislikes :)')))
    # print('view_count : %s' %(meta['view_count']))
    # print( 'id          : %s' %(meta['id']))
    # print( 'format      : %s' %(meta['format']))
    # print( 'duration    : %s' %(meta['duration']))
    # print( 'title       : %s' %(meta['title']))
    # print('description : %s' %(meta['description']))
    # print('webpage_url_basename : %s' %(meta['webpage_url_basename']))
    # print("current_app : %s" %(current_app.root_path))
    print("Download & FFMpeg-speed= ", str(time_diff))

    yt_metadata_json = {
        'upload date' : meta['upload_date'],
        'uploader'    : meta['uploader'],
        'view_count'  : meta['view_count'],
        'id'          : meta['id'],
        'format'      : meta['format'],
        'duration'    : meta['duration'],
        'title'       : meta['title'],
        'description' : meta['description'],
        'webpage_url_basename': meta['webpage_url_basename'],
        "current_app": current_app.root_path,
        "download_time": str(time_diff),
    }
    # print("trimmed yt_metadata_json:")
    # print(yt_metadata_json)
    print ("meta")
    print ("meta")
    print ("meta")
    print ("meta")
    print ("meta")
    # print (meta)
    # if vidUrl == "https://www.twitch.tv/videos/28138895":
    if vidUrl == "https://www.twitch.tv/videos/5057810":
        try:
            x = json.dumps(meta)
            return x
        except:
            print("except done")
            return "execpt... done meta"
    return meta

def downloadChannelsAudio(scrapped_channels_with_todos):
    metadata_Ytdl_list = []
    chnLimit = 0
    for channel in scrapped_channels_with_todos:
        chnLimit = chnLimit + 1
        if chnLimit == 2:
            break
        print ("downloading this channel_with_todos...............................................")
        print (channel)
        i = 0
        for link in channel['todos']:
            i = i + 1
            if i == 3:
                break
            metadata = downloadTwtvVid(link, True)
            metadata_Ytdl = Md_Ytdl.Metadata_Ytdl(channel['url'], link, metadata)
            metadata_Ytdl_list.append(metadata_Ytdl)
            print("metadata_Ytdl=" + str(metadata_Ytdl))
            try:
                jsonstr1 = json.dumps(metadata_Ytdl.__dict__)
                # print("jsonstr1="+ str(jsonstr1))
            except:
                print("failed to dump: " + metadata_Ytdl.username + " @ " + metadata_Ytdl.link + " - Fail" )
            print("completed: " + metadata_Ytdl.username + " @ " + metadata_Ytdl.link)
        
        print()
        print()
        print()
        print()
        print()
        print()
        print("metadata_Ytdl_list")
        print(metadata_Ytdl_list)
        print(" FINSIHED DOWNLAOINDG (2 vids) from channels[todos]:")
        print(" FINSIHED DOWNLAOINDG (2 vids) from channels[todos]:")
        # for x in metadata_Ytdl_list:
            # print (x)
            # print (json.dumps(x.__dict__))
        print()
        print()
        print()
        print()
        print()
        print()
        print("metadata_Ytdl_list")
        print(metadata_Ytdl_list)
    return metadata_Ytdl_list

def createCaptionsWhisperAi(metadata_Ytdl):
    output_local_dir = "assets/raw"
    output_local_dir = "./assets/raw"
    print("#############                         #############")
    print("############# createCaptionsWhisperAi #############")
    print("#############                         #############")
    isPass = False

    for requested in metadata_Ytdl.metadata.get('requested_downloads', []):
        print(requested.get('format_id', {}))
        if requested.get('format_id') == "Audio_Only": # TODO othe audio_ids like youtube's, ect
            __finaldir = requested.get('__finaldir') # "C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids"
            filepath = requested.get("filepath")     # "C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids\\Bootcamp to Challenger \uff5c-v1747933567.f_Audio_Only.mp3"
            filename = filepath.replace(__finaldir, "")
            filename = filename[1:] if (filename[0] == "/" or filename[0] == "\\") else filename # filename = "Bootcamp to Challenger \uff5c-v1747933567.f_Audio_Only.mp3"

            # ffmpeg convertion to audio doesnt change extension -.-
            filename = (filename[:-4] + ".mp3") if filename[-4:] == ".mp4" else filename # NOTE position of ":" is diff

            output_full_dir = "{}/{}/{}".format(current_app.root_path, output_local_dir, filename)
            print ("---------------> ADDING " + filename)
            print ("@  " + output_full_dir)
            print(filename)
            # NEED TO UPLOAD FILE FROM DIRECTORY TO BUCKET
            isPass = whispererAiFAST.mp3FastTranscribe(filename)
        
    return isPass


def uploadAudioToS3(metadata, keybase):
    s3 = boto3.client('s3')
    filesToSave = []
    print("upload audto to s3() ************************************************")
    print("upload audto to s3() ************************************************")
    print("upload audto to s3() ************************************************")
    print("upload audto to s3() ************************************************")
    print("upload audto to s3() ************************************************")
    print("upload audto to s3() ************************************************")
    print("upload audto to s3() ************************************************")
    print("upload audto to s3() ************************************************")
    print(metadata.get('requested_downloads', []))
    for requested in metadata.get('requested_downloads', []):
        print(requested.get('format_id', {}))
        if requested.get('format_id') == "Audio_Only":
            __finaldir = requested.get('__finaldir') # "C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids"
            filepath = requested.get("filepath")     # "C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids\\Bootcamp to Challenger \uff5c-v1747933567.f_Audio_Only.mp3"
            filename = filepath.replace(__finaldir, "")
            filename = filename[1:] if (filename[0] == "/" or filename[0] == "\\") else filename # filename = "Bootcamp to Challenger \uff5c-v1747933567.f_Audio_Only.mp3"
            print ("filename[-4:]")
            print ("filename[-4:]")
            print ("filename[-4:]")
            print ("filename[-4:]")
            print ("filename[-4:]")
            print (filename[-4:])
            print (len(filename[-4:]))
            print (filename[-4:] == ".mp4")
            filename = (filename[:-4] + ".mp3") if filename[-4:] == ".mp4" else filename # NOTE position of ":" is diff
            if filename:
                print ("---------------> ADDING " + filename)
                filesToSave.append(filename)
        
    # NEED TO UPLOAD FILE FROM DIRECTORY TO BUCKET
    for file in filesToSave:
        metaKey = keybase + "/metadta.json"
        fileKey =  keybase + '/' + file
        print("")
        print("file=" + file)
        print("fileKey=" + fileKey)
        print("metaKey=" + metaKey)
        print("")
        try:
            s3.upload_file(fname, BUCKET_NAME, fileKey)
            print ("UPLOADED !!!!!!!!!!!!!!!!! ")
            if file == filesToSave[-1]:
                s3.put_object(
                    Body=json.dumps(metadata),
                    Bucket=BUCKET_NAME,
                    Key= metaKey  # channels/test/raw/2023-15/2.json
                )
        except Exception as e:
            print("oops! " + str(e))
            return False
    return True

def updateScrapeHistory(yt_metadata_json):
    if yt_metadata_json is None:
        return
    already_downloaded_json = getAlreadyDownloaded(yt_metadata_json['uploader'])
    s3 = boto3.client('s3')
    s3.put_object(
        Body=json.dumps(yt_metadata_json),
        Bucket=BUCKET_NAME,
        Key=S3_ALREADY_DL_KEYBASE + yt_metadata_json['uploader']
    )
    print( "done: \n")



def getAlreadyDownloaded(username):
    s3 = boto3.client('s3')
    
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_ALREADY_DL_KEYBASE)['Contents']
    print("sorted_objects = == = = == = = =")
    for obj in objects:
        print(obj)
        print ("key split " + str(obj['Key'].split(',')))
        print(username)
        if ( not username in obj['Key'].split(',')):
            return None
    
    responseGetObj = s3.get_object(
        Bucket = BUCKET_NAME,
        Key = S3_ALREADY_DL_KEYBASE + username # ex) 'channels/scrapped/lolgeranimo.json'
    )
    
    binary_data = responseGetObj['Body'].read()
    print(":D len(dataz)=" + str(len(binary_data)))

    json_string = binary_data.decode('utf-8')
    json_object = json.loads(json_string) # { "data":[ { "viewminutes":932768925, "streamedminutes":16245, ... } ] }
    print("GOT THIS------------")
    print(json_object)
    return json_object


def addTodoDownloads(scrapped_channels):
    print("getTodoDownloads - start")
    # todo_downloads_objlist = []
    for channel in scrapped_channels:
        print("000000000000000000000000000000000000000000000000")
        print(channel)
        already_downloaded = yt.getAlreadyDownloaded(channel['url'])
        print("already_downloaded")
        print(already_downloaded)
        print() 
        # Probably a better way to write this :/
        # If the scrapped links doesnt exist in our already_downloaded list then add to todos
        todo_downloads = []
        for link in channel['links']:
            if already_downloaded is None:
                todo_downloads = channel['links']
                break
            if not link in already_downloaded:
                todo_downloads.append(link)
        channel['todos'] = todo_downloads
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

