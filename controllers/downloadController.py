from __future__ import unicode_literals

import time
import asyncio
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from flask import jsonify
import requests

# use selenium to render the page and then scrape it with beautiful soup. 
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-web-page-into-python
import re

options = Options()
# options.add_argument('--headless')
options.add_argument('--window-size=1550,1250') # width, height
browser = None
channel = "lolgeranimo"

def aggregateChannels(url):
    print("url")
    print(url)
    # url = "https://jsonplaceholder.typicode.com/posts/1"
    url = "https://jsonplaceholder.typicode.com/todos"
    # url = "https://sullygnome.com/api/tables/channeltables/getchannels/30/0/0/3/desc/0/100"
    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }
    response = requests.get(url, headers=headers)

    print ('reponse code = ' + str(response.status_code))
    print ('reponse code = ' + str(response.status_code))
    print ('reponse code = ' + str(response.status_code))
    print (response)
    print ('')
    print (response.headers)
    print ('')
    print (response.reason)
    print ('')
    print (response.text)
    if response.status_code >= 200 and response.status_code < 300:
        json_data = response.json()
        print(json_data)
        for obj in json_data:
            print("=========================")
            print(obj)
            if obj.language:
                print(obj.language)
            if obj.viewminutes:
                print(obj.viewminutes)
            if obj.displayname:
                print(obj.displayname)
            if obj.ur:
                print(obj.url)
    else:
        print(f'Error: {response.status_code}')
    return "nice :)"

async def scrapePage(channel):    
    global browser
    print("browser")
    print(browser)
    if browser is None:
        print(browser)
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    # loop = asyncio.get_event_loop()
    return await scrapePageGogo(channel)
    # loop = asyncio.new_event_loop()
    # loop.run_until_complete(gera())
    # loop.close()

async def scrapePageGogo(channel):
    # channel = "lolgeranimo"
    url = f'https://www.twitch.tv/{channel}/videos?filter=archives&sort=time'
    browser.get(url)

    # using selenium scroll to the bottom of the page to load all the videos.
    print (browser.title)
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    loopMax = 1
    for i in range(loopMax):
        print ("scroll to bottom " + str(i))
        browser.execute_script("""document.querySelector("[id='root'] main .simplebar-scroll-content").scroll(0, 10000)""")
        time.sleep(3)
    
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    browser.quit()

    vids = soup.select("a[href^='/videos/']")
    # print ("vids")
    # print (vids)
    allHrefs = []
    for tag in vids:
        allHrefs.append(tag['href'])
        print ("tag['href']=" + tag['href'])
    # allHrefs.sort()
    hrefsSet = set()
    for href in allHrefs:
        match = re.search(r'(/videos/\d+)(\?.*)', href)
        if match:
            print (match.group(1))
            hrefsSet.add(match.group(1))

    # print ("hrefsSet")
    # print ("hrefsSet")
    # [print (hrefsSet) for hrefsSet in enumerate(hrefsSet)]

    unique_list = list(set(hrefsSet))
    resultz = list(unique_list)
    # resultz = jsonify(results=unique_list)
    print ("resultz")
    print (resultz)
    return resultz
