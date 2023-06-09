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
import env_app as env_varz
import mocks.initScrapData
import re
import os
import time


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


def scrape4VidHref(channels, isDebug=False): # gets returns -> {...} = [ { "displayname":"LoLGeranimo", "url":"lolgeranimo", "links":[ "/videos/1758483887", "/videos/1747933567",...
    channelMax = int(env_varz.SELENIUM_NUM_CHANNELS_DEBUG) if env_varz.IS_DEBUG == "True" else int(env_varz.SELENIUM_NUM_CHANNELS)
    if isDebug and os.getenv("ENV") == "local":
        channels = mocks.initScrapData.getScrapeData()
    global browser
    SLEEP_SCROLL = 3
    NUM_BOT_SCROLLS = 1
    print("browser")
    print(browser)
    if browser is None:
        print(browser)
        # browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        # firefox_profile = webdriver.FirefoxProfile()
        # firefox_profile.set_preference("media.block-play-until-visible", False)
        # firefox_profile.set_preference("media.autoplay.blocking_policy", 5)
        # firefox_profile.set_preference("media.autoplay.default", 1)
        # firefox_profile.set_preference("media.autoplay.enabled.user-gestures-needed", False)
        # firefox_profile.set_preference("media.autoplay.block-event.enabled", True)        
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    everyChannel = []
    cnt = 0
    for channel in channels:
        cnt = cnt + 1
        if cnt > channelMax:
            browser.quit()
            return everyChannel
        url = f'https://www.twitch.tv/{channel["url"]}/videos?filter=archives&sort=time'
        browser.get(url)
        print ("--------------------")
        print (cnt)
        print (browser.title)
        time.sleep(2)
        browser.execute_script(scriptPauseVidsJs)
        for i in range(NUM_BOT_SCROLLS):
            print ("scroll to bottom " + str(i))

            browser.execute_script("window.scrollTo(0,document.body.scrollHeight)") # scroll to the bottom, load all the videos.
            browser.execute_script("""document.querySelector("[id='root'] main .simplebar-scroll-content").scroll(0, 10000)""")
            time.sleep(SLEEP_SCROLL)
        
        # Scrap a[href] via BeautifulSoup
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        vids = soup.select("a[href^='/videos/']:has(img)")
        allHrefs = []
        for tag in vids:
            inner_text = tag.get_text(separator="|").lower()
            print("SOUP - get_text() =" + inner_text )
            # Skip very recent broadcasts, b/c they might currently be streaming (incomplete vod)
            # TODO bugs may occure for marathon vids (_isVidFinished)
            if ( not (("hours" in inner_text) or ("minutes" in inner_text))):
                match = re.search(r'(/videos/\d+)(\?.*)', tag['href'])
                if match and tag['href'] not in allHrefs:
                    print (match.group(1))
                    allHrefs.append(match.group(1))
            else:
                print ("skipping a['href'] @ text=" + tag['href'])

        resultz = allHrefs

        everyChannel.append({
            'displayname': channel["displayname"],
            'language': channel["language"], # English
            'logo': channel["logo"], 
            'twitchurl': channel["twitchurl"], # https://www.twitch.tv/lolgeranimo
            'url': channel["url"], # url = lolgeranimo
            'links': resultz # '/videos/5057810
        })
        # resultz = jsonify(results=unique_list)
        print ("resultzzzzz")
        print (resultz)
    print ("============= everyChannel ================")
    print ("============= everyChannel ================")
    print ("============= everyChannel ================")
    print ("============= everyChannel ================")
    print (everyChannel)
    print (everyChannel)
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
