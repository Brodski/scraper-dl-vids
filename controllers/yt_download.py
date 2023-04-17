from flask import Blueprint, current_app
import yt_dlp
import time

import boto3
import json
import datetime
import controllers.yt_download as yt
import models.Metadata_Yt as Metadata_Yt

import os

CURRENT_DATE_YMD = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
BUCKET_NAME = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket'
directory_name = 'mydirectory' # this directory legit exists in this bucket ^
directory_name_real = "channels/ranking/raw" 
S3_ALREADY_DL_KEYBASE = 'channels/scrapped/'
# S3_ALREADY_DL_KEY = 'channels/scrapped/lolgeranimo/2023-04-01.json'

test_bp = Blueprint('test', __name__)
vidUrl = 'https://www.twitch.tv/videos/1783465374' # pro leauge
vidUrl = 'https://www.twitch.tv/videos/1791750006' # lolgera
# vidUrl = 'https://www.twitch.tv/videos/1792255936' # sub only
vidUrl = 'https://www.twitch.tv/videos/1792342007' # live

# Download
#  https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L137-L312
def downloadUrl(link, isDownload=False): 
    vidUrl = "https://www.twitch.tv" + link
    print ("getMeta vidUrl=" + vidUrl)
    ydl_opts = {
        # 'format': 'sb0,sb1,sb2,Audio_Only/600/250/worstvideo/bestaudio/160p30',
        'format': 'Audio_Only/600/250/bestaudio/worstvideo/160p30',
        # 'outtmpl': '{}/%(title)s-%(id)s.f%(format_id)s.%(ext)s'.format(current_app.root_path),
        "outtmpl": "%(title)s-%(id)s.f_%(format_id)s.%(ext)s",
        "verbose": True,
        # "concurrent_fragment_downloads": 8
    }
    print ("getMeta vidUrl=")
    print ("getMeta vid.output=" + '{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path))
    print (vidUrl)
    # return "gg"
    # YES https://www.twitch.tv/videos/1778309747?filter=archives&sort=time
    # NO  https://www.twitch.tv/lolgeranimo/videos/1778309747

    start_time = time.time()
    # Inferior alterative to yt_dlp is youtube_dl
    # `with youtube_dl.YoutubeDL(ydl_opts) as ydl:`
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(vidUrl, download=isDownload) 
        except Exception as e:
            print ("Failed to extract vid info:")
            print (e)
            return None

    end_time = time.time() 
    time_diff = end_time - start_time
    print('--------------------')
    # print('meta %s' %(meta))
    # print('meta %j' %(meta))
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
    # metaData_yt = Metadata_Yt(yt_metadata_json)
    print(yt_metadata_json)
    return meta
    # return yt_metadata_json

def downloadChannelsAudio(scrapped_channels_with_todos):
    each_channels_and_their_ytdl_vids_metadata = []
    scrapped_channels_metadata = []
    for channel in scrapped_channels_with_todos:
        print ("downloading...............................................")
        print (channel)
        channel_ytdl_metadata = []
        i = 0
        for link in channel['todos']:
            i = i + 1
            if i == 3:
                break
            metadata = downloadUrl(link, True)
            uploadFilesToS3(metadata)
            channel_ytdl_metadata.append(metadata)
        # msg = downloadUrl(links[0], True)
        # for link in links:
        #     downloadUrl(base_url, link)
        each_channels_and_their_ytdl_vids_metadata.append(channel_ytdl_metadata)
    return each_channels_and_their_ytdl_vids_metadata



def uploadFilesToS3(metadata):
    s3 = boto3.client('s3')
    filesToSave = []
    for requested in metadata.get('requested_downloads', []):
        filename = requested.get('format_id', {}).get('_filename', {})
        if filename:
            filesToSave.append(filename)
        
    # NEED TO UPLOAD FILE FROM DIRECOTYR TO BUCKET
    for fname in filesToSave:
        s3.put_object(
            Body=json.dumps(json_object),
            Bucket=BUCKET_NAME,
            Key= s3_key_test + str(0) + ".json" # channels/test/raw/2023-15/2.json
            # Key=s3_key
        )
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

