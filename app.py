from __future__ import unicode_literals
from flask import Flask
# from aioflask import Flask
# import asyncio

# import requests 
# from bs4 import BeautifulSoup
# from requests_html import AsyncHTMLSession

# import youtube_dl
import yt_dlp

import time


app = Flask(__name__)

@app.route('/')
def home():
    # Links to all other routes in the app.
    return """
    <h1>Links to all other routes in the app.</h1>
    <ul>
        <li><a href="/yo">/yo (Hello World)</a></li>
        <li><a href="/yt">/yt (downloads a vid)</a></li>
        <li><a href="/yt1">/yt1 (extract_info a vid) </a></li>
        <hr/>
        <li><a href="/gera">/gera gera stuff RIP </a></li>
        <li><a href="/test">/test (scrapes ycombinator) RIP </a></li>
    </ul>

    """

@app.route('/yo/<text>')
@app.route('/yo/')
def yo(text="brother"):

    return "Yo {} @ {}".format(text, app.root_path)

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


@app.route('/yt/')
def yt():

    ydl_opts = {
        # 'format': 'bestaudio/best',
        # 'format': 'worstvideo+bestaudio',
        # 'format': '(worstvideo+bestaudio)',
        'format': 'worstvideo/bestaudio',
        # 'format': 'worst',
        'output': '{}/%(title)s-%(id)s.%(ext)s'.format(app.root_path),
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
    start_time = time.time()
    
    print("GOGOGOOG---start", start_time)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(['https://www.twitch.tv/videos/1693915459'])
        # ydl.download(['https://www.twitch.tv/videos/1683425427'])
        # ydl.download(['https://www.youtube.com/watch?v=9bZkp7q19f0'])
         
    end_time = time.time() 
    print("GOGOGOOG ---- end", end_time)
    print("time-diff ---- ", end_time - start_time )

@app.route('/yt1/')
def yt1():
    
    ydl_opts = {
        'format': 'worstvideo/bestaudio',
        'output': '{}/%(title)s-%(id)s.%(ext)s'.format(app.root_path),
        "verbose": True
    }

    # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        #  https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L137-L312
        meta = ydl.extract_info(
            'https://www.twitch.tv/videos/1693915459', download=True) 
            # 'https://www.youtube.com/watch?v=9bZkp7q19f0', download=True) 

    # print('meta : %s' %(meta))
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
    return 'bam'
if __name__ == "__main__":
    app.run(debug=True)

