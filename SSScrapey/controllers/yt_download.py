from flask import Blueprint, current_app
from flask import jsonify, abort
from models.Metadata_Ytdl import Metadata_Ytdl
import boto3
import controllers.yt_download as yt
import env_app as env_varz
import json
import os
import subprocess
import time
import urllib.parse
import yt_dlp

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

def getTitle(meta):
    if meta.get('title'):
        title = meta.get('title')
    elif meta.get('requested_downloads')[0].get('title'):
        title = meta.get('title')[0].get('title')
    else: 
        title = meta.get('fulltitle') 
    return title

# Download
#  https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L137-L312
# TODO???
# Turn this into (HTTP REQUEST ---> Lambda)
def downloadTwtvVid(link:str, isDownload=True): 
    print ("000000000000                  00000000000000000")
    print ("000000000000 download twtvVid 00000000000000000")
    print ("000000000000                  00000000000000000")
    # vidUrl = 'https://www.twitch.tv/videos/1783465374' # pro leauge
    # vidUrl = 'https://www.twitch.tv/videos/1791750006' # lolgera
    # # vidUrl = 'https://www.twitch.tv/videos/1792255936' # sub only
    # vidUrl = 'https://www.twitch.tv/videos/1792342007' # live
    # https://www.twitch.tv/videos/28138895
    output_local_dir = "assets/audio"
    vidUrl = link if "youtube.com" in link.lower() else "https://www.twitch.tv/videos" + link
        
    try:
        output_template = '{}/{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path, output_local_dir)
    except:
        output_template = '{}/{}/%(title)s-%(id)s.%(ext)s'.format(os.getcwd()+'/', output_local_dir)
    ydl_opts = {
        # format --> https://github.com/yt-dlp/yt-dlp#sorting-formats
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
        "parse_metadata" "requested_downloads.filepath:%(filepath):"  # my custom  metadata field
        "overwrites": True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0', #https://trac.ffmpeg.org/wiki/Encode/MP3
        #     # 'preferredquality': '192', #https://trac.ffmpeg.org/wiki/Encode/MP3
        #                                 #https://github.com/ytdl-org/youtube-dl/blob/195f22f679330549882a8234e7234942893a4902/youtube_dl/postprocessor/ffmpeg.py#L302
        }],
    }
    print("vidUrl")
    print(vidUrl)
    print(vidUrl)
    start_time = time.time()
    print("doing ytdl extract/download stuff")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(vidUrl, download=isDownload) 
        except Exception as e:
            print ("Failed to extract vid!!: " + vidUrl + " : " + str(e))
            return None
    print('--------TOP-----------x')
    print('  (dlTwtvVid) Download complete: time=' + str(time.time() - start_time))
    meta = removeNonSerializable(meta)
    filepath = meta.get('requested_downloads')[0].get('filepath')  #C:\Users\SHAAAZAM\scraper-dl-vids\assets\audio\Calculated-v5057810.mp3
    title = getTitle(meta)
    inFile = "file:" + filepath
    if env_varz.WHSP_EXEC_FFMPEG == "True":
        outFile =  "".join(inFile.split(".")[:-1]) + ".opus" #opus b/c of the ffmpeg cmd below
    else:
        outFile = inFile
    
    print("  (dlTwtvVid) getMeta vidUrl= " + vidUrl)
    print("  (dlTwtvVid) getMeta vid.output= " + output_template)
    print("  (dlTwtvVid) filepath= "+filepath)
    print("  (dlTwtvVid) title= "+title)
    print("  (dlTwtvVid) inFile= "+inFile)
    print("  (dlTwtvVid) outFile= "+outFile)
    print("")

    # https://superuser.com/questions/1422460/codec-and-setting-for-lowest-bitrate-ffmpeg-output
    #  ffmpeg -i '.\Adc Academy - Informative Adc Stream - GrandMaster today？ [v1792628012].mp3' -c:a libopus -ac 1 -ar 16000 -b:a 33K -vbr constrained gera33k.opus
    # ffmpeg_command = [ 'ffmpeg', '-i', inFile, '-q:a', '0', '-map', 'a', inFile+'.mp3' ]
    # if env_varz.WHSP_EXEC_FFMPEG:
    #     _execFFmpegCmd(ffmpeg_command)
    ffmpeg_command = [
        # 'ffmpeg', '-version'
        # 'ffmpeg', '-y', '-i', inFile, '-filter:a', 'atempo=1.5', outFile
        'ffmpeg', '-y', '-i',  inFile, '-c:a', 'libopus', '-ac', '1', '-ar', '16000', '-b:a', '10K', '-vbr', 'constrained', outFile
    ]
    if env_varz.WHSP_EXEC_FFMPEG == "True":
        _execFFmpegCmd(ffmpeg_command)
    
    end_time = time.time() 
    time_diff = end_time - start_time
    
    print("     Download + FFMpeg cmd = ", str(time_diff))
    print('---------BOT----------x')
    return meta, outFile
    
    
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
# Recieves the sullygnome processed data
def bigBoyChannelDownloader(scrapped_channels_with_todos,*, isDebug):
    print ("000000000000                         00000000000000000")
    print ("000000000000 bigBoyChannelDownloader 00000000000000000")
    print ("000000000000                         00000000000000000")

    # CONFIG VARS
    chn_limit =          int(env_varz.YTDL_NUM_CHANNELS_DEBUG)     if isDebug or (env_varz.IS_DEBUG and os.getenv("ENV") == "local") else int(env_varz.YTDL_NUM_CHANNELS)
    vid_download_limit = int(env_varz.YTDL_VIDS_PER_CHANNEL_DEBUG) if isDebug or (env_varz.IS_DEBUG and os.getenv("ENV") == "local") else int(env_varz.YTDL_VIDS_PER_CHANNEL)

    for chn in scrapped_channels_with_todos:
        print("    (bigboy) Will do these channels: " + chn.get('url'))

    metadata_Ytdl_list = []
    chn_counter = 0
    for channel in scrapped_channels_with_todos:
        if chn_counter == chn_limit:
            break
        chn_counter = chn_counter + 1
        
        print ("    (bigboy) ----> TOP -" + str(chn_counter))
        print ("    (bigboy) ----> Channel: " + channel.get("url") + " ---> number todos = " + str(len(channel.get("todos"))))
        print ("    (bigboy) ----> " + str(channel))
        todo_count = 0
        for link in channel['todos']:
            if todo_count == vid_download_limit:
                break
            todo_count = todo_count + 1
            print ("    (bigboy) ----> chn #" + str(chn_counter) + " todo_count: " + str(todo_count))
            print ("    (bigboy) ----> " + channel.get("url") + " @ " + link)
            metadata, outFile = downloadTwtvVid(link, True)
            if metadata == None:
                continue
            metadata_Ytdl = Metadata_Ytdl(channel['url'], channel['displayname'], channel['language'], channel['logo'], channel['twitchurl'], link, outFile, metadata) # Meta(lolgeranimo, /video/12345123, {... really big ... })
            metadata_Ytdl_list.append(metadata_Ytdl)
            print("    (bigboy) completed: " + metadata_Ytdl.link + " @ " + metadata_Ytdl.channel)
        
        print()
        print("    (bigboy) metadata_Ytdl_list:")
        print("    (bigboy) " + str (metadata_Ytdl_list))
        print()
    return metadata_Ytdl_list

#  --> channels/vod-audio/<CHN>/<DATE>/<ID>.mp3
def uploadAudioToS3(yt_meta: Metadata_Ytdl):
    print ("000000000000                 00000000000000000")
    print ("000000000000 uploadAudioToS3 00000000000000000")
    print ("000000000000                 00000000000000000")
    # caption_keybase = channels/vod-audio/lolgeranimo/1747933567 

    meta = yt_meta.metadata
    vod_title = os.path.basename(yt_meta.outFile)

    display_id = meta.get('display_id')
    ext = meta.get("requested_downloads")[0].get('ext')

    vod_id = yt_meta.link.replace("/videos/", "").replace("/", "")
    caption_keybase = env_varz.S3_CAPTIONS_KEYBASE + yt_meta.channel + "/" + vod_id
    vod_filename = vod_title #+ "-" + display_id + "." + ext
    vod_encode = urllib.parse.quote(vod_filename)
    s3fileKey = caption_keybase + "/" + vod_encode
    s3metaKey = caption_keybase + "/metadata.json"
    vod_decode = urllib.parse.unquote(vod_encode)
    print("")
    print("    (uploadAudioToS3) " + str(yt_meta.metadata)[:100])
    print("    (uploadAudioToS3) uploading: " +yt_meta.channel)
    print("    (uploadAudioToS3) link: " + yt_meta.link)
    # print("  (uploadAudioToS3)   filepath:" + meta.get('requested_downloads')[0].get('filepath'))
    print("    (uploadAudioToS3) meta.get(fulltitle)= " + meta.get('fulltitle'))
    print("    (uploadAudioToS3) meta.get(display_id)= " + meta.get('display_id'))
    print("    (uploadAudioToS3) ext = " + ext)
    print("    (uploadAudioToS3) filepath= " + vod_title)
    print("    (uploadAudioToS3) vod_filename = " + vod_filename)
    print("    (uploadAudioToS3) vod_filename encode= " + vod_encode)
    print("    (uploadAudioToS3) vod_filename de encode= " + vod_decode )
    print("    (uploadAudioToS3) s3fileKey= " + s3fileKey)
    print("    (uploadAudioToS3) metaKey= " + s3metaKey)
    print("")
    s3 = boto3.client('s3')
    try:
        # uploads: channels/vod-audio/lck/2023-04-18/576354726/metadta.json
        # uploads: channels/vod-audio/lck/2023-06-02/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.mp3
        print ("    UPLOADING MP3 !!!!!!!!!!!!!!!!! ")
        print ("    " + yt_meta.outFile[5:])
        s3.upload_file(os.path.abspath(yt_meta.outFile[5:]), env_varz.BUCKET_NAME, s3fileKey)
        print ("    UPLOADING META !!!!!!!!!!!!!!!!! ")
        s3.put_object(Body=json.dumps(yt_meta.__dict__, default=lambda o: o.__dict__), Bucket=env_varz.BUCKET_NAME, Key=s3metaKey)
        return True
    except Exception as e:
        print("oops! " + str(e))
        return False
    

















    
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################


###############################################################
#                                                             #
# Get From s3, eg channels/scrapped/lolgeranimo.json
# returns some json
def getAlreadyDownloadedS3(channel, links):
    print ("xxxxxxxxxxxx                        xxxxxxxxxxxx")
    print ("xxxxxxxxxxxx getAlreadyDownloadedS3 xxxxxxxxxxxx")
    print ("xxxxxxxxxxxx                        xxxxxxxxxxxx")
    print("links")
    print(links)
    links_ids = [link.replace("videos/", "") + "/" for link in links]
    print("links_ids")
    print(links_ids)
    s3 = boto3.client('s3')
    
    try:
        the_prefix = env_varz.S3_CAPTIONS_KEYBASE + channel
        print("     (getAlreadyDownloadedS3) channel: "+ channel)
        print("     (getAlreadyDownloadedS3) key: " + the_prefix)
        responseGetObj = s3.list_objects_v2(Bucket = env_varz.BUCKET_NAME, Prefix= the_prefix)['Contents'] # ex) channels/vod-audio/lolgeranimo/
        responseGetObj = sorted(responseGetObj, key=lambda obj: obj['LastModified'])
        print(links_ids)
        print(links_ids)

        for id in links_ids:
            for obj in responseGetObj:
                print("     (getAlreadyDownloadedS3) obj[Key]= " + f"{obj['Key']}")
                if id in obj['Key']:
                    print("YES!")
                    print(id)
                    print(obj['Key'])
                    links_ids.remove(id)
                    print(links_ids)

        # for obj in responseGetObj:
        #     print("     (getAlreadyDownloadedS3) obj[Key]= " + f"{obj['Key']}")
        #     for id in links_ids:
        #         if id in obj['Key']:
        #             print("YES!")
        #             print(id)
        #             print(obj['Key'])
        #             links_ids.remove(id)
        #             print(links_ids)
        print(links_ids)
        print(links_ids)
        print(links_ids)
        print(links_ids)
        print(links_ids)
    except Exception as e:
        print("     (getAlreadyDownloadedS3) found nothing!")
        print(e)
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print("links")
        print([link.replace("videos/", "") + "/" for link in links])
        return [link.replace("videos/", "") + "/" for link in links]
        
    print("    (getAlreadyDownloadedS3) GOT THIS------------")
    print(links_ids)
    return links_ids
#                                                           #
#############################################################


def getAlreadyDownloadedS3_TEST(channel, linkz):
    x = getAlreadyDownloadedS3(channel, linkz)
    if x:
        return x
    else: 
        abort(404, description="Username not found")

# Make sure we havent already DL the vid
def addTodoListS3(scrapped_channels):
    print ("000000000000                      000000000000")
    print ("000000000000     addTodoListS3    000000000000")
    print ("000000000000                      000000000000")
    print("    (addTodoS3) Making sure we havent already DL'd the vid")
    cnt = 0
    for scrap_channel in scrapped_channels:
        print(str(cnt) + " (addTodoS3) TOP ---------")
        print(scrap_channel)
        cnt = cnt + 1
        todo_vod_ids = yt.getAlreadyDownloadedS3(scrap_channel['url'], scrap_channel['links']) # url = lolgeranimo, links = ['/videos/5057810', '/videos/28138895']
        scrap_channel['todos'] = todo_vod_ids # B/c reference
        print(str(cnt) + " (addTodoS3) BOT ---------")
    return scrapped_channels