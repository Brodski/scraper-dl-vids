from flask import Blueprint, current_app
import yt_dlp
import time

import boto3
import json
import datetime
import controllers.yt_download as yt
import models.Metadata_Yt as Metadata_Yt
import models.Metadata_Ytdl as Md_Ytdl
# from models.Metadata_Ytdl import Metadata_Ytdl

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
def downloadTwtvVid(link, isDownload=False): 
    vidUrl = "https://www.twitch.tv" + link
    print ("000000000000                  00000000000000000")
    print ("000000000000 download twtvVid 00000000000000000")
    print ("000000000000                  00000000000000000")
    ydl_opts = {
        # format --> https://github.com/yt-dlp/yt-dlp#sorting-formats
        # 'format': 'sb0,sb1,sb2,Audio_Only/600/250/worstvideo/bestaudio/160p30',
        'format': 'Audio_Only/600/250/bestaudio/worstvideo/160p30',
        # 'outtmpl': '{}/%(title)s-%(id)s.f%(format_id)s.%(ext)s'.format(current_app.root_path),
        "outtmpl": "%(title)s-%(id)s.f_%(format_id)s.%(ext)s",
        # "verbose": True,
        # "concurrent_fragment_downloads": 8
        'keepvideo': True,
        # 'nopostoverwrites': True,
        # 'postprocessors': [{
        #     'key': 'FFmpegExtractAudio',
        #     'preferredcodec': 'mp3',
        # }]
    }
    print ("getMeta vidUrl=" + vidUrl)
    print ("getMeta vidUrl=" + vidUrl)
    print ("getMeta vidUrl=" + vidUrl)
    print ("getMeta vidUrl=" + vidUrl)
    print ("getMeta vid.output=" + '{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path))
    # return "gg"
    # YES https://www.twitch.tv/videos/1778309747?filter=archives&sort=time
    # NO  https://www.twitch.tv/lolgeranimo/videos/1778309747

    start_time = time.time()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(vidUrl, download=isDownload) 
        except Exception as e:
            print ("Failed to extract vid info:")
            print (e)
            return None

    end_time = time.time() 
    time_diff = end_time - start_time
    print('--------------------x')
    print(meta)
    print('upload date : %s' %(meta['upload_date']))
    print( 'uploader    : %s' %(meta['uploader']))
    print( 'views       : %d' %(meta['view_count']))
    print( 'likes       : %s' %(meta.get('like_count', 'nope :o')))
    print( 'dislikes    : %s' %(meta.get('dislike_count', 'no dislikes :)')))
    print('view_count : %s' %(meta['view_count']))
    print( 'id          : %s' %(meta['id']))
    print( 'format      : %s' %(meta['format']))
    print( 'duration    : %s' %(meta['duration']))
    print( 'title       : %s' %(meta['title']))
    print('description : %s' %(meta['description']))
    print('webpage_url_basename : %s' %(meta['webpage_url_basename']))
    print("current_app : %s" %(current_app.root_path))
    print("time-diff ---- ", str(time_diff))

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
    return meta
    # return yt_metadata_json

def downloadChannelsAudio(scrapped_channels_with_todos):
    scrapped_channels_ytmd_objs = []
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
            scrapped_channels_ytmd_objs.append(metadata_Ytdl)
            print("metadata_Ytdl")
            print("metadata_Ytdl")
            print("metadata_Ytdl")
            print("metadata_Ytdl")
            print("metadata_Ytdl")            
            print(metadata_Ytdl)
            print(metadata_Ytdl)
            jsonstr1 = json.dumps(metadata_Ytdl.__dict__)
            print("jsonstr1")
            print("jsonstr1")
            print(jsonstr1)
            # createCaptionsWhisperAi() # (lolgeranimo, 12341234, {...})

            keybase = S3_CAPTIONS_KEYBASE + channel['url'] + "/" + CURRENT_DATE_YMD + link.replace("/videos", "") # channels/captions/lolgeranimo/2023-04-18/1747933567
            print ("KEY CAPTIONS=" + keybase)
            print ("KEY CAPTIONS=" + keybase)
            
            # uploadAudioToS3(metadata, keybase) # key = upload 'location' in the s3 bucket 
            # getAlreadyDownloaded
        
        print()
        print()
        print()
        print()
        print()
        print()
        print("scrapped_channels_ytmd_objs")
        print(scrapped_channels_ytmd_objs)
        print(" FINSIHED DOWNLAOINDG (2 vids) from channels[todos]:")
        print(" FINSIHED DOWNLAOINDG (2 vids) from channels[todos]:")
        for x in scrapped_channels_ytmd_objs:
            print (x)
            print (json.dumps(x.__dict__))
        print()
        print()
        print()
        print()
        print()
        print()
        print("scrapped_channels_ytmd_objs")
        print(scrapped_channels_ytmd_objs)
    return scrapped_channels_ytmd_objs



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
            filename = requested.get('_filename')
            if filename:
                filesToSave.append(filename)
        
    # NEED TO UPLOAD FILE FROM DIRECOTYR TO BUCKET
    for fname in filesToSave:
        metaKey = keybase + "/metadta.json"
        fileKey =  keybase + '/' + fname
        print("")
        print("fname=" + fname)
        print("fileKey=" + fileKey)
        print("metaKey=" + metaKey)
        print("")
        try:
            s3.upload_file(fname, BUCKET_NAME, fileKey)
            print ("UPLOADED !!!!!!!!!!!!!!!!! ")
            s3.put_object(
                Body=json.dumps(metadata),
                Bucket=BUCKET_NAME,
                Key= metaKey  # channels/test/raw/2023-15/2.json
                # Key=s3_key
            )
        except Exception as e:
            print("oops!")
            continue
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

