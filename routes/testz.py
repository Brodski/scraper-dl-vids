from flask import Blueprint, current_app
import yt_dlp
import time


test_bp = Blueprint('test', __name__)
vidUrl = 'https://www.twitch.tv/videos/1783465374'

# Download
#  https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L137-L312
@test_bp.route('/yt1')
def test_editor():
    
    ydl_opts = {
        'format': 'worstvideo/bestaudio',
        'output': '{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path),
        "verbose": True
    }

    start_time = time.time()
    # Inferior alterative to yt_dlp is youtube_dl
        # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(vidUrl, download=True) 
    end_time = time.time() 
    print('--------------------')
    print('upload date : %s' %(meta['upload_date']))
    print( 'uploader    : %s' %(meta['uploader']))
    print( 'views       : %d' %(meta['view_count']))
    print( 'likes       : %s' %(meta.get('like_count', 'nope')))
    print( 'dislikes    : %s' %(meta.get('dislike_count', 'no dislikes')))
    print( 'id          : %s' %(meta['id']))
    print( 'format      : %s' %(meta['format']))
    print( 'duration    : %s' %(meta['duration']))
    print( 'title       : %s' %(meta['title']))
    print('description : %s' %(meta['description']))
    print("current_app : %s" %(current_app.root_path))
    print("GOGOGOOG ---- end", end_time)
    print("time-diff ---- ", end_time - start_time )
    time_diff = end_time - start_time
    msg = "done with time =" + str(time_diff)
    return msg







##############################################################
# This is exactly the same as above but with commented out stuff for reference
@test_bp.route('/yt2')
def test_yt_dlp():
    ydl_opts = {
        # 'format': 'bestaudio/best',
        # 'format': 'worstvideo+bestaudio',
        # 'format': '(worstvideo+bestaudio)',
        # 'format': 'worst',
        'format': 'worstvideo/bestaudio',
        'output': '{}/%(title)s-%(id)s.%(ext)s'.format(current_app.root_path),
        "verbose": True,
        # "listformats": True,
        # 'postprocessors': [{
        #     'key': 'FFmpegExtractAudio',
        #     'preferredcodec': 'mp3',
        #     'preferredquality': '0', #https://trac.ffmpeg.org/wiki/Encode/MP3
            # 'preferredquality': '192', #https://trac.ffmpeg.org/wiki/Encode/MP3
                                        #https://github.com/ytdl-org/youtube-dl/blob/195f22f679330549882a8234e7234942893a4902/youtube_dl/postprocessor/ffmpeg.py#L302
        # }],
        # 'logger': MyLogger(),
        # 'progress_hooks': [my_hook],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([vidUrl])
    return "done"


@test_bp.route('/date')
def test_date():
    return 'Blog Date'













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