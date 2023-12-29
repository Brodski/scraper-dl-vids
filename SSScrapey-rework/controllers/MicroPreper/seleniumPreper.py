from __future__ import unicode_literals
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import env_file as env_varz
import mocks.initScrapData
from models.ScrappedChannel import ScrappedChannel
import re
import os
import time
from typing import List

###
# Assembly AI multi lingual speech recognition
# https://www.assemblyai.com/blog/how-to-run-openais-whisper-speech-recognition-model/#whisper-advanced-usage
# it links here too --> https://github.com/openai/whisper/blob/main/notebooks/Multilingual_ASR.ipynb
#
###

######################################################################################### 
######################################################################################### 
#
# Use selenium and beautiful soup to scrape the vods for 1000 channels
#
######################################################################################### 
######################################################################################### 
options = Options()
if env_varz.SELENIUM_IS_HEADLESS == "True":
    options.add_argument('--headless')
    os.environ["MOZ_HEADLESS"] = "1"

# options.add_argument('--autoplay-policy=no-user-gesture-required')
options.add_argument('–-autoplay-policy=user-required') 
options.add_argument('--window-size=1550,1250') # width, height
options.add_argument('--disable-features=PreloadMediaEngagementData, MediaEngagementBypassAutoplayPolicies') # width, height
# chrome_prefs = {
#     "profile.default_content_setting_values.autoplay": 2,  # 2 means Block autoplay
# }
# options.add_experimental_option("prefs", chrome_prefs)
browser = None


scriptPauseVidsJs = """
    const stopIt = (vid) => {
        vid.pause()
    };
    console.log("document.querySelectorAll('video')")
    console.log(document.querySelectorAll('video'))
    for ( let vid of document.querySelectorAll('video')) {
        console.log(vid)
        if (vid != null) {
            stopIt(vid);
            vid.addEventListener("play", (e) => {
                stopIt(vid)
            })
        }
    }
"""

def scrape4VidHref(channels:  List[ScrappedChannel], isDebug=False): # gets returns -> {...} = [ { "displayname":"LoLGeranimo", "name_id":"lolgeranimo", "links":[ "/videos/1758483887", "/videos/1747933567",...
    channelMax = int(env_varz.SELENIUM_NUM_CHANNELS)
    vodsMax = int(env_varz.SELENIUM_NUM_VODS)
    SLEEP_SCROLL = 2
    NUM_BOT_SCROLLS = 2
    everyChannel:List[ScrappedChannel] = []
    cnt = 0
    browser = None

    # browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("media.block-play-until-visible", False)
    firefox_profile.set_preference("media.autoplay.blocking_policy", 5)
    firefox_profile.set_preference("media.autoplay.default", 1)
    firefox_profile.set_preference("media.autoplay.enabled.user-gestures-needed", False)
    firefox_profile.set_preference("media.autoplay.block-event.enabled", True)        
    
    try:
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install(), options=options, firefox_profile=firefox_profile))
        for channel in channels:
            cnt = cnt + 1
            if cnt > channelMax:
                break
            url = f'https://www.twitch.tv/{channel.name_id}/videos?filter=archives&sort=time'
            print(url)
            browser.get(url)
            print ("--------------------")
            print (str(cnt) + ": " + browser.title)
            time.sleep(2)
            browser.execute_script(scriptPauseVidsJs)
            for i in range(NUM_BOT_SCROLLS):
                browser.execute_script("window.scrollTo(0,document.body.scrollHeight)") # scroll to the bottom, load all the videos.
                browser.execute_script("""document.querySelector("[id='root'] main .simplebar-scroll-content").scroll(0, 10000)""")
                time.sleep(SLEEP_SCROLL)
            
            # Scrape <a href> via BeautifulSoup
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            vids = soup.select("a[href^='/videos/']:has(img)")
            allHrefs = []
            for tag in vids:
                inner_text = tag.get_text(separator="|").lower()
                # Skip very recent broadcasts, b/c they might currently be streaming (incomplete vod)
                # TODO bugs may occure for marathon vids (_isVidFinished)
                if ( not (("hours" in inner_text) or ("minutes" in inner_text))):
                    match = re.search(r'(/videos/\d+)(\?.*)', tag['href'])
                    if match and tag['href'] not in allHrefs:
                        allHrefs.append(match.group(1)) # /videos/1983739230
                else:
                    print("skipping a['href'] @ text=" + tag['href'])
            channel.links = allHrefs[:vodsMax]
            everyChannel.append(channel)
            print(channel)
    except Exception as e:
        print("An error occurred :(")
        print(f"{e}")
    finally:
        # Ensure the browser is closed even if an error occurs
        if browser:
            browser.quit()
    return everyChannel


# When multi-day marathon
# def _isVidFinished(inner_text):
#     # inner_text = tag.get_text(separator="|")
#     print("SOUP - get_text() =" + inner_text )
#     dayz = None
#     broadcast_time = None
#     for i, item in enumerate(inner_text.split("|")):
#         print(item)
#         print(len(item))
#         if "days" in item:
#             dayz = item
#         if len(item) >=8 and item.count(":") == 2:
#             broadcast_time = item.split(":")[0]
#     if broadcast_time and dayz:
#             days_num = int( dayz.split("days")[0].strip() )
#             broadcast_hours = broadcast_time.split(":")[0]
#             if (days_num*24) < broadcast_hours:
#                 print("NOT KOSHER!!!!!!" )
