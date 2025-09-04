from __future__ import unicode_literals
import traceback
from bs4 import BeautifulSoup
from models.ScrappedChannel import ScrappedChannel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.service import Service as FirefoxService
from typing import List
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import env_file as env_varz
import mocks.initHrefsData
import os
import re
import time
import logging
from utils.logging_config import LoggerConfig

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()

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
if env_varz.PREP_SELENIUM_IS_HEADLESS == "True":
    options.add_argument('--headless')
    os.environ["MOZ_HEADLESS"] = "1"

# options.add_argument('--autoplay-policy=no-user-gesture-required')
options.add_argument('--autoplay-policy=user-required') 
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

def isPersonOnline(soup: BeautifulSoup):
    isOnline = False
    online_ele_1 = soup.select(".home-live-player-overlay--contents")
    online_ele_2 = soup.select(".home-live-player-overlay")
    online_ele_3_profile = soup.select(".user-avatar-card__live ")
    offline_ele = soup.select(".channel-root__player--offline")
    player_ele = soup.select(".channel-root__player ")

    # logger.debug("  (isPersonOnline) online_ele_1 length: " +  len(online_ele_1))
    # logger.debug("  (isPersonOnline) online_ele_2 length: " +  len(online_ele_2))
    # logger.debug("  (isPersonOnline) online_ele_3_profile length: " +  len(online_ele_3_profile))
    # logger.debug("  (isPersonOnline) offline_ele length: " +  len(offline_ele))
    # logger.debug("  (isPersonOnline) player_ele length (should be 1): " +  len(player_ele))

    player_ele = soup.select(".channel-root__player ")
    if player_ele[0] and player_ele[0].get_text(strip=True).lower().startswith("live"):
        logger.debug("  (isPersonOnline) YES!!!!!!")
        isOnline = True
    if len(online_ele_1) + len(online_ele_2) + len(online_ele_3_profile) > 0:
        logger.debug("  (isPersonOnline) YES!!!!!!2")
        isOnline = True
    logger.debug("  (isPersonOnline) isOnline: " +  str(isOnline))
    return isOnline

def scrape4VidHref(channels:  List[ScrappedChannel], isDebug=False): # gets returns -> {...} = [ { "displayname":"Geranimo", "name_id":"geranimo", "links":[ "/videos/1758483887", "/videos/1747933567",...
    # channelMax = int(env_varz.PREP_SELENIUM_NUM_CHANNELS)
    channelMax = int(env_varz.NUM_CHANNELS)
    vodsMax = int(env_varz.NUM_VOD_PER_CHANNEL)
    SLEEP_SCROLL = 2
    NUM_BOT_SCROLLS = 2
    everyChannel:List[ScrappedChannel] = []
    cnt = 0
    browser = None
    # if isDebug:
    #     # scrapped_channels: List[ScrappedChannel] = mocks.initHrefsData.getHrefsData()
    #     # logger.debug(json.dumps(scrapped_channels, default=lambda o: o.__dict__, indent=4))
    #     # return scrapped_channels

    #     # new debug
    #     # return jd_onlymusic, nmplol, geranimo
    #     return channels[:channelMax]

    logger.debug('A running. scrap4vid.........')
    # browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("media.block-play-until-visible", False)
    firefox_profile.set_preference("media.autoplay.blocking_policy", 5)
    firefox_profile.set_preference("media.autoplay.default", 1)
    firefox_profile.set_preference("media.autoplay.enabled.user-gestures-needed", False)
    firefox_profile.set_preference("media.autoplay.block-event.enabled", True)        

    try:
        logger.debug('B running. scrap4vid.........')
        browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install(), options=options, firefox_profile=firefox_profile))
        logger.debug(f"Selenium: Getting {channelMax} channels. Getting {vodsMax} vods per channel")
        for channel in channels:
            if cnt >= channelMax:
                break
            cnt = cnt + 1
            url = f'https://www.twitch.tv/{channel.name_id}/videos?filter=archives&sort=time'
            browser.get(url)
            idx_print = url.find('?filter')
            print ("--------------------")
            print (str(cnt) + ": " + browser.title)
            logger.debug(url[:idx_print])
            time.sleep(4)
            browser.execute_script(scriptPauseVidsJs)
            for i in range(NUM_BOT_SCROLLS):
                browser.execute_script("window.scrollTo(0,document.body.scrollHeight)") # scroll to the bottom, load all the videos.
                browser.execute_script("""
                    function getAllScrollableElements(root = document.body) {
                        const scrollables = [];
                        const elements = root.getElementsByTagName("*");

                        for (let el of elements) {
                            const style = window.getComputedStyle(el);
                            const overflowY = style.overflowY;
                            const isScrollableY = overflowY === 'auto' || overflowY === 'scroll';
                            const canScrollY = el.scrollHeight > el.clientHeight;

                            if (isScrollableY && canScrollY) {
                            scrollables.push(el);
                            }
                        }

                        return scrollables;
                    }

                    const scrollables = getAllScrollableElements();

                    scrollables.forEach(el => {
                        el.scrollTop = el.scrollHeight;
                    });
                """)
                time.sleep(SLEEP_SCROLL)
            
            # Scrape <a href> via BeautifulSoup
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            isOnline = isPersonOnline(soup)
            vids = soup.select("a[href^='/videos/']:has(img)")
            allHrefs = []
            for idx, tag in enumerate(vids):
                if idx == 0 and isOnline:
                    continue # if guy is streaming, skip the current vod
                match = re.search(r'(/videos/\d+)(\?.*)', tag['href'])
                if match and tag['href'] not in allHrefs:
                    allHrefs.append(match.group(1)) # /videos/1983739230

            channel.links = allHrefs[:vodsMax]
            everyChannel.append(channel)
            logger.debug(f"Got {len(channel.links)} vids for {browser.title}")
    except Exception as e:
        logger.error("An error occurred :(")
        logger.error(f"{e}")
        stack_trace = traceback.format_exc()
        logger.error(stack_trace)
    finally:
        # Ensure the browser is closed even if an error occurs
        if browser:
            browser.quit()
    return everyChannel
