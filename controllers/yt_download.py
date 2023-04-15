from flask import Blueprint, current_app
import yt_dlp
import time

import boto3
import json
import datetime

import os

current_week = str(datetime.date.today().isocalendar()[1])
current_year = str(datetime.date.today().isocalendar()[0])
s3_key_test = "channels/test/raw/" + current_year + "-" + current_week + "/"
BUCKET_NAME = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket'
directory_name = 'mydirectory' # this directory legit exists in this bucket ^
directory_name_real = "channels/ranking/raw" 

test_bp = Blueprint('test', __name__)
vidUrl = 'https://www.twitch.tv/videos/1783465374' # pro leauge
vidUrl = 'https://www.twitch.tv/videos/1791750006' # lolgera
# vidUrl = 'https://www.twitch.tv/videos/1792255936' # sub only
vidUrl = 'https://www.twitch.tv/videos/1792342007' # live

# Download
#  https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L137-L312
def getMeta(base_url, link): 
    vidUrl = base_url + link
    print ("getMeta vidUrl=" + vidUrl)
    ydl_opts = {
        'format': 'worstvideo/bestaudio',
        'output': '{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path),
        "verbose": True
    }
    print ("getMeta vidUrl=")
    print ("getMeta vid.output=" + '{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path))
    print (vidUrl)
    return "gg"

    start_time = time.time()
    # Inferior alterative to yt_dlp is youtube_dl
    # `with youtube_dl.YoutubeDL(ydl_opts) as ydl:`
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(vidUrl, download=False) 
        except Exception as inst:
            print ("Failed to extract vid info:")
            print (inst)
            return "rip"

    end_time = time.time() 
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
    print("time-diff ---- ", end_time - start_time )
    time_diff = end_time - start_time
    msg = "done with time =" + str(time_diff)
    return msg







##############################################################
# This is exactly the same as above but with commented out stuff for reference
def downloadAudio(base_url, link):
    vidUrl = base_url + link
    ydl_opts = {
        'format': 'worstvideo/bestaudio',
        'output': '{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path),
        "verbose": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([vidUrl])
    return "done"

def downloadChannelAudio(base_url, links):
    msg = getMeta(base_url, links[0])
    # for link in links:
    #     getMeta(base_url, link)
    return msg