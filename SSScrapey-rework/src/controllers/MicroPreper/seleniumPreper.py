from __future__ import unicode_literals
import traceback
from bs4 import BeautifulSoup
from models.ScrappedChannel import ScrappedChannel
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from typing import List
from webdriver_manager.firefox import GeckoDriverManager
from env_file import env_varz
import mocks.initHrefsData
import os
import re
import time
import logging
from utils.logging_config import LoggerConfig
from utils.emailer import sendEmail

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
WIDTH = 1450
HEIGHT = 1050
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


everyChannel:List[ScrappedChannel] = []
def scrape4VidHref(channels:  List[ScrappedChannel], index=0, retry_count=0): # gets returns -> {...} = [ { "displayname":"Geranimo", "name_id":"geranimo", "links":[ "/videos/1758483887", "/videos/1747933567",...
    channelMax = int(env_varz.PREP_NUM_CHANNELS)
    vodsMax = int(env_varz.PREP_NUM_VOD_PER_CHANNEL)
    SLEEP_SCROLL = 2
    NUM_BOT_SCROLLS = 2
    MAX_RETRY = 3
    # everyChannel:List[ScrappedChannel] = []
    index_aux = index
    browser = None

    logger.debug('A running. scrap4vid.........')
    firefox_profile = FirefoxProfile()
    firefox_profile.set_preference("media.block-play-until-visible", False)
    firefox_profile.set_preference("media.autoplay.blocking_policy", 5)
    firefox_profile.set_preference("media.autoplay.default", 1)
    firefox_profile.set_preference("media.autoplay.enabled.user-gestures-needed", False)
    firefox_profile.set_preference("media.autoplay.block-event.enabled", True)        

    options = Options()
    options.add_argument('--autoplay-policy=user-required') 
    options.add_argument(f'--window-size={WIDTH},{HEIGHT}')
    options.add_argument('--disable-features=PreloadMediaEngagementData, MediaEngagementBypassAutoplayPolicies') # width, height
    if env_varz.PREP_SELENIUM_IS_HEADLESS == "True":
        options.add_argument('--headless')
        os.environ["MOZ_HEADLESS"] = "1"
    # options.add_argument('--autoplay-policy=no-user-gesture-required')
    options.profile = firefox_profile

    channel: ScrappedChannel = None
    try:
        logger.debug('B running. scrap4vid.........')
        logger.debug(f"Selenium: Getting {channelMax} channels. Getting {vodsMax} vods per channel")
        service = FirefoxService(GeckoDriverManager().install())
        browser = webdriver.Firefox(service=service, options=options)
        browser.set_window_size(WIDTH, HEIGHT)
        # for channel in channels:
        channel: ScrappedChannel = None
        for i in range(index, len(channels)):
            print(f"i={i}, index={index}")
            index_aux = i
            channel: ScrappedChannel = channels[i]
            
            url = f'https://www.twitch.tv/{channel.name_id}/videos?filter=archives&sort=time'
            browser.get(url)
            idx_print = url.find('?filter')
            logger.debug(channel.name_id)
            logger.debug("  " + url[:idx_print])
            time.sleep(2)
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
                if i < NUM_BOT_SCROLLS - 1:
                    time.sleep(SLEEP_SCROLL)
            
            # Scrape <a href> via BeautifulSoup
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            isOnline = isPersonOnline(soup)
            vids = soup.select("a[href^='/videos/']:has(img)")
            allHrefs = []
            for idx, tag in enumerate(vids):
                if idx == 0 and isOnline:
                    continue # if guy is streaming, skip the current vod. (TODO if your a coward like geranimo you dont auto publish vods, and the first vod will get skipped)
                match = re.search(r'(/videos/\d+)(\?.*)', tag['href'])
                if match and tag['href'] not in allHrefs:
                    allHrefs.append(match.group(1)) # /videos/1983739230

            retry_count = 0 # reset
            channel.links = allHrefs[:vodsMax]
            everyChannel.append(channel)
            logger.debug(f"  Got {len(channel.links)} vids for {browser.title}")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error("An error occurred :(")
        logger.error(stack_trace)
        logger.error(f"env_varz.PREP_SELENIUM_IS_HEADLESS={env_varz.PREP_SELENIUM_IS_HEADLESS}")
        if retry_count < MAX_RETRY:
            logger.info("🚷 BANNED CHANNEL? or some error occured, trying again...")
            msg_ = ""
            if channel:
                msg_ = msg_ + channel.name_id
            if url and idx_print:
                msg_ = msg_ + ":  " + url[:idx_print]
            logger.info(msg_)
            time.sleep(10)
            scrape4VidHref(channels, index_aux + 1, retry_count + 1)
        if retry_count >= MAX_RETRY:
            ### SUBJECT
            subject = f"Preper {os.getenv('ENV')} - (SCRAPE) Failed selenium scrap on a channel"
            ### BODY
            msg = f"Attempted but failed url={url}\n"
            msg = msg + f"⚠ Maybe a banned channel??? \n"
            msg = msg + f"Execeptions:\n"
            msg = msg + f"f{e}\n"
            logger.error(msg)
            sendEmail(subject, msg)
    finally:
        # Ensure the browser is closed even if an error occurs
        if browser:
            browser.quit()
    return everyChannel
