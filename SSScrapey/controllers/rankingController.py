from __future__ import unicode_literals

import time
from typing import List, Tuple, Dict
# import asyncio
# from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from flask import jsonify, abort
import requests

import boto3
import json

import env_app as env_varz

# # # # # # # # # # # GAMEPLAN  # # # # # # # # # # # # # # # # # # # # # #
#                                                                         # 
# Lambda function (likely ... TBD):                                       # 
#                                                                         # 
# Once a day                                                              # 
# Http request top 100 channels from third party website                  # 
    # process it slightly                                                 # 
# Selenium scrape urls from twitch                                        # 
# Ytdl download vods from channels                                        # 
    # Convert to audio and reduce bitrate/file-size                       # 
# Upload audio to s3                                                      # 
# Update a json of all the completed mp3 downloads                        # 
# Update a joson of all the completed captions                            # 
# todo = audio_downloads - completed_captions                             # 
#                                                                         # 
# VAST.AI / GPU                                                           # 
# (spin a docker container that does this):                               # 
# Get Json file of the to-do audio files                                  # 
# Download the audio from my s3                                           # 
# WhisperFast.py on audio                                                 # 
# Upload transcripions                                                    # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #




####################################################################################
#                                                                 type3=most watched
#                                                   /30days/0?/#clicks?/type/desc/start/get100streams
#  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/1/3/desc/0/100
#  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/2/3/desc/100/100
#  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/3/3/desc/200/100
#  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/4/3/desc/300/100
#  https://sullygnome.com/api/tables/channeltables/getchannels/30/0/1/5/desc/0/100
                                            # type6=avg-viewers
# https://sullygnome.com/api/tables/channeltables/getchannels/30/0/11/6/desc/0/100
# https://sullygnome.com/api/tables/channeltables/getchannels/30/0/1/3/desc/0/10
# https://sullygnome.com/api/tables/channeltables/getchannels/30/0/2/3/desc/10/10
# https://sullygnome.com/api/tables/channeltables/getchannels/30/0/3/3/desc/20/10



######################################################################################### 
######################################################################################### 
#
# Make simple http request to sully gnome's api, use that data for top 1000 channels
#
######################################################################################### 
######################################################################################### 


VIP_LIST = [
    {
        "displayname": "LoLGeranimo",
        "language": "English",
        "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
        "twitchurl": "https://www.twitch.tv/lolgeranimo",
        "url": "lolgeranimo"
    }
  ]
def getTopChannels(*, numChannels=50): # Returns big json: { "data": [ { "avgviewers": 53611, "displayname": "xQc", ...
    print ("000000000000                         00000000000000000")
    print ("000000000000 getTopChannels - sully  00000000000000000")
    print ("000000000000                         00000000000000000")
    if numChannels > 300 or (numChannels % 10) != 0:
        print("Error, numChannels is too big or not in 10s: " + str(numChannels))
        return
    loopMax = int((numChannels / 10))
    # pageSize = 100
    pageSize = 10
    type = 3 # note '3' => enum = Most watched
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }
    accumilator = []
    complete_json = { "data": accumilator}
    for i in range(loopMax):
        startAt = (i * pageSize) # for their api
        # url = 'https://sullygnome.com/api/tables/channeltables/getchannels/30/0/0/3/desc/0/100'
        url = (f'https://sullygnome.com/api/tables/channeltables/getchannels/30/0/{str(i)}/{type}/desc/{str(startAt)}/{str(pageSize)}')
        print ("    (getTopChannels) ----------------------")
        print ("    " + url)
        print ("    (getTopChannels) ----------------------")

        response = requests.get(url, headers=headers)

        print ('    (getTopChannels) reponse code = ' + str(response.status_code))
        print ('    (getTopChannels) response.reason: ' + str(response.reason))
        print ('    (getTopChannels) size: ' + str(len(response.content)))
        # print ("response.text =" + response.text)
        print ()
        if response.status_code >= 200 and response.status_code < 300:
            res_json = response.json()
            if 'data' in res_json:
                data = res_json['data']
                cnt = 0
                accumilator.extend(data)
                for obj in data:
                    print("    (getTopChannels) " + str(i) + " @ "+ str(cnt) + ": ===========")
                    print('    ' + str(obj))
                    print('    (getTopChannels) userId=' + str(obj.get('userId')))
                    print('    (getTopChannels) language=' + str(obj.get('language')))
                    print('    (getTopChannels) viewminutes=' + str(obj.get('viewminutes')))
                    print('    (getTopChannels) displayname=' + str(obj.get('displayname')))
                    print('    (getTopChannels) url=' + str(obj.get('url')))
                    print('    (getTopChannels) logo=' + str(obj.get('logo')))
                    cnt= cnt + 1
        else:
            print(f'Error: {response.status_code}')
    print ("    (getTopChannels) DONE!")
    # print (complete_json)
    return complete_json


def tidyData(json_object):
    relevant_list = []
    for channel in json_object['data']: # json_object =getTopChannelsAndSaveResponse.json
        # quasi way of making a set, but afraid one of those other properties might change. ALso, trying to avoid forloop
        relevant_entry = {
            "displayname": channel.get('displayname'),
            "twitchurl": channel.get('twitchurl'),
            "language": channel.get('language'),
            "logo": channel.get('logo'),
            "url": channel.get('url'),
        }
        relevant_list.append(relevant_entry)
    return relevant_list

def addVipList(channels):
    for channel in VIP_LIST:
        channels.insert(0,channel)
    return channels


