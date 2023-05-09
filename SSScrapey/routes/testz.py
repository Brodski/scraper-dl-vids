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
vidUrl = 'https://www.twitch.tv/videos/1792628012' # lolgera
# # vidUrl = 'https://www.twitch.tv/videos/1792255936' # sub only
# vidUrl = 'https://www.twitch.tv/videos/1792342007' # live
vidUrl = "https://www.youtube.com/watch?v=rQsAxHHEHaw" # Belmont gains
vidUrl = 'https://www.twitch.tv/videos/1792628012' # lolgera
vidUrl = 'https://www.youtube.com/watch?v=qOoe3ZpciI0' # AI scared
vidUrl = 'https://www.twitch.tv/videos/1767827635' # short gera

# Download
# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L137-L312
@test_bp.route('/yt1')
def test_editor():
    
    ydl_opts = {
        'format': 'worstvideo/bestaudio',
        'output': '{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path),
        "verbose": True,
        "concurrent_fragment_downloads": 8
        # "cookies": "cookieTime.txt"
    }
    # local storage, "mature=true"
    print ("getMeta vidUrl=")
    print ("getMeta vid.output=" + '{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path))
    print (vidUrl)
    start_time = time.time()
    # Inferior alterative to yt_dlp is youtube_dl
    # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(vidUrl, download=True) 
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
@test_bp.route('/yt2')
def test_yt_dlp():
    ydl_opts = {
        # 'format': 'worstvideo+bestaudio',
        # 'format': '(worstvideo+bestaudio)',
        'output': '{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path),
        "verbose": True,
        # "listformats": True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            # 'preferredquality': '0', #https://trac.ffmpeg.org/wiki/Encode/MP3
            # 'preferredquality': '192', #https://trac.ffmpeg.org/wiki/Encode/MP3
                                        # https://github.com/ytdl-org/youtube-dl/blob/195f22f679330549882a8234e7234942893a4902/youtube_dl/postprocessor/ffmpeg.py#L302
        }],
        # 'logger': MyLogger(),
        # 'progress_hooks': [my_hook],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([vidUrl])
    return "done"









@test_bp.route('/yt3')
def test_yt_dlp3():
    ydl_opts = {
        # 'format': 'worstvideo+bestaudio',
        # 'format': '(worstvideo+bestaudio)',
        'format': 'sb0,sb1,sb2,Audio_Only/600/250/worstvideo/bestaudio/160p30',
        # 'output': '{}/%(title)s-%(id)s.f%(format_id)s.%(ext)s'.format(current_app.root_path),
        "outtmpl": "%(title)s-%(id)s.f_%(format_id)s.%(ext)s",
        "verbose": True,
        # "extractaudio": True,
        # "audioformat": "mp3",
        # "listformats": True,
        # "listsubtitles": True,
        # "writesubtitles":  "./subtitlez.txt",
        # "writesubtitles":   '{}/SUBSS+%(title)s-%(id)s.%(ext)s'.format(current_app.root_path),
        # "writesubtitles":   True,
        # "allsubtitles": True,
        # 'postprocessors': [{
        #     'key': 'FFmpegExtractAudio',
        #     'preferredcodec': 'mp3',
        # #     'preferredquality': '0', #https://trac.ffmpeg.org/wiki/Encode/MP3
        # #     # 'preferredquality': '192', #https://trac.ffmpeg.org/wiki/Encode/MP3
        # #                                 #https://github.com/ytdl-org/youtube-dl/blob/195f22f679330549882a8234e7234942893a4902/youtube_dl/postprocessor/ffmpeg.py#L302
        # }],
        # 'logger': MyLogger(),
        # 'progress_hooks': [my_hook],
    }
    # vidUrl = 'https://www.youtube.com/watch?v=qOoe3ZpciI0' # AI scared
    meta = 123
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(vidUrl, download=True) 
        # meta = ydl.download([vidUrl])
    return str(meta)





##############################################################
# This is exactly the same as above but with commented out stuff for reference
@test_bp.route('/yt4')
def test_yt_dl_paudio():
    ydl_opts = {
        'format': 'sb0,sb1,sb2,Audio_Only/600/250/bestaudio/worstvideo/160p30',
        "outtmpl": "%(title)s-%(id)s.f_%(format_id)s.%(ext)s",
        "verbose": True,
        "writethumbnail": True,
        "embedthumbnail": True,
        # "extractaudio": True,
        # "listformats": True,
    }
    # vidUrl = 'https://www.youtube.com/watch?v=qOoe3ZpciI0' # AI scared
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        zz = ydl.download([vidUrl])
    return str(zz)
















@test_bp.route('/date')
def test_date():
    return 'Blog Date'

@test_bp.route('/getAllS3Jsons')
def getAllS3Jsons():
    # "LastModified": datetime.datetime(2023,4,10,7,44,12,"tzinfo=tzutc()
    # obj['Key']          = channels/ranking/raw/2023-15/100.json
    # obj['LastModified'] = Last modified: 2023-04-11 06:54:39+00:00
    s3 = boto3.client('s3')
    objList = []
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=directory_name_real)
    print ("objects")
    print (objects)
    print (objects.get('Contents'))
    if objects.get('Contents') is None:
        return "NOTHIGN!"
    objects = objects['Contents']

    for obj in objects:
        objList.append(obj)
    sorted_objects = sorted(objList, key=lambda obj: obj['LastModified'])
    print ("objList")
    print ("objList")
    print (objList)
    print("-----SORTED----")
    for obj in sorted_objects:
        print(f"{obj['Key']} - Last modified: {obj['LastModified']}")

        
    x = datetime.datetime(2023, 4, 11, 6, 54, 39, 0, tzinfo=datetime.timezone.utc)
    filtered_objects = filter(lambda obj: obj['LastModified'] > x, sorted_objects)
    print("-----FILTER ----")
    print (x)
    for obj in filtered_objects:
        print(f"{obj['Key']} - Last modified: {obj['LastModified']}")
        
    return objects




@test_bp.route('/getAllS3Jsons')
def uploadJsonToS3Test():
    s3 = boto3.client('s3')
    myJsonStff = { 
        "someArry": [
            { 
                "hello": "hello dude",
                "goodbye": "get out of here"
            },
            { 
                "party": "party hard",
                "gottaRock": "I wanna rock n roll",
                "gottaRock2": "I wanna rock n roll all night!"
            }
        ],
        "bangbang": "Pop boom bang! ka bam!"
    }
    json_object = myJsonStff
    s3.put_object(
        Body=json.dumps(json_object),
        Bucket=BUCKET_NAME,
        Key= s3_key_test + str(0) + ".json" # channels/test/raw/2023-15/2.json
        # Key=s3_key
    )
    return "done: \n" + str(myJsonStff)



@test_bp.route('/doS3Stuff')
def doS3Stuff():
    s3Aws = os.environ.get('BUCKET_NAME')
    s3local = os.environ.get('BUCKET_NAME_LOCAL')
    print(f'AWS_BUCKET Key: {s3Aws}')
    print(f'BUCKET_NAME_LOCAL Key: {s3local}')

    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=directory_name)['Contents']

    for obj in objects:
        print(obj['Key'])
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=directory_name) 
    print (response)
    print('================')
    print('================')
    print('================')
    print('================')
    for content in response.get('Contents', []):
        object_key = content.get('Key')
        print (object_key)
        # local_file_path = 'local/path/to/save/' + object_key.split('/')[-1]
        # s3.download_file(BUCKET_NAME, object_key, local_file_path)
    print('================')
    responseGetObj = s3.get_object(
            Bucket = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket',
            # Key = 'mydirectory/twitch-stuff.json'
            Key = 'mydirectory/testiq.png'
        )
    dataz = responseGetObj['Body'].read()
    print("len(dataz)=" + str(len(dataz)))
    return s3local


@test_bp.route('/testGetTop500Channels_NameCompleted')
def testGetTop500Channels_NameCompleted():
    json_files = ['./mocks/0to100channels.json', './mocks/100to200channels.json']

    # Read and parse JSON files
    json_data = []
    for json_file in json_files:
        with open(json_file, 'r', encoding="utf8") as file:
            data = json.load(file)
            print(f"Contents length of file data = {len(data.get('data'))}:")
        print(data.get('thisdoesnotexist'))
        json_data.extend(data.get('data'))
        # print(f"Contents of {json_file}:")
        # print(data)
    print (';;;;;;;;;;;;;;;;;;')
    print (';;;;;;;;;;;;;;;;;;')
    print (';;;;;;;;;;;;;;;;;;')
    for dude in json_data:
        print (dude.get("displayname"))
    return json_data


#####
#####
#####  Bullshit below
#####  Bullshit below
#####
#####

    
# @app.route('/gera/')
# async def gera():
#     channel = "lolgeranimo"
#     url = f'https://www.twitch.tv/{channel}/videos?filter=archives&sort=time'
#     session = AsyncHTMLSession()    
#     res = await session.get(url)
#     await res.html.arender()
#     return "links"


# @app.route('/test/')
# def test():
#     res = requests.get('https://news.ycombinator.com/news')
#     print(res)
#     soup = BeautifulSoup(res.text, 'html.parser')    
#     print(soup)
#     links = soup.select('.titleline')
#     print(links)
#     subtext = soup.select('.subtext')
#     def create_custom_hn(links, subtext):
#         hn = []
#         for idx, item in enumerate(links):
#             title = links[idx].getText()
#             href = links[idx].get('href', None)
#             vote = subtext[idx].select('.score')
#             if len(vote):
#                 points = int(vote[0].getText().replace(' points', ''))
#                 if points > 99:
#                     hn.append({'title': title, 'link': href, 'votes': points})
#         return hn
#     def print_results(hnlist):
#         for idx, item in enumerate(hnlist):
#             print('{}. {} - {} points'.format(idx, item['title'], item['votes']))
#     hn = create_custom_hn(links, subtext)
#     print_results(hn)

#     return "Test"