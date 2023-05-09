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
