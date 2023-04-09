from __future__ import unicode_literals
# from flask import Flask
# from aioflask import Flask

import requests 
from bs4 import BeautifulSoup
# from requests_html import HTMLSession
# from requests_html import AsyncHTMLSession

# import youtube_dl
# import yt_dlp

import time
import asyncio

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# use selenium to render the page and then scrape it with beautiful soup. 
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-web-page-into-python

# https://stackoverflow.com/questions/6028000/how-to-read-a-static-web-page-into-python
import sys
import re


###
# Assembly AI multi lingual speech recognition
# https://www.assemblyai.com/blog/how-to-run-openais-whisper-speech-recognition-model/#whisper-advanced-usage
# it links here too --> https://github.com/openai/whisper/blob/main/notebooks/Multilingual_ASR.ipynb
#
###

options = Options()
# options.add_argument('--headless')
options.add_argument('--window-size=1550,1250') # width, height
browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
# Dimension dem = new Dimension(750,450);
# driver.manage().window().setSize(dem);


async def gera():
    channel = "lolgeranimo"
    url = f'https://www.twitch.tv/{channel}/videos?filter=archives&sort=time'
    # session = HTMLSession()
    # res = session.get(url)    
    # res.html.render(sleep=2)
    browser.get(url)
    # using selenium scroll to the bottom of the page to load all the videos.

    # print (browser.page_source)
    print (browser.title)
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(3)
    print ("scroll to bottom 1")
    browser.execute_script("""document.querySelector("[id='root'] main .simplebar-scroll-content").scroll(0, 10000)""")
    time.sleep(3)
    print ("scroll to bottom 2")
    browser.execute_script("""document.querySelector("[id='root'] main .simplebar-scroll-content").scroll(0, 10000)""")
    time.sleep(3)
    
    
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    browser.quit()
    vids = soup.select("a[href^='/videos/']")
    print ("vids")
    print (vids)
    allHrefs = []
    for tag in vids:
        allHrefs.append(tag['href'])
        print ("tag['href']=" + tag['href'])

    hrefsSet = set()
    for href in allHrefs:
        match = re.search(r'(/videos/\d+)(\?.*)', href)
        if match:
            hrefsSet.add(match.group(1))

    print ("hrefsSet")
    [print (hrefsSet) for hrefsSet in enumerate(hrefsSet)]

    return "links"


    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(gera())
    loop.close()

