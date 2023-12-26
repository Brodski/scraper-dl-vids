from __future__ import unicode_literals

import time
from typing import List, Tuple, Dict
from models.ScrappedChannel import ScrappedChannel
# import asyncio
# from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from flask import jsonify, abort
import requests
import controllers.seleniumController as seleniumController

import boto3
import json
import os

import env_file as env_varz




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


def doItAllSully(*, isDebug=False, isEnd=False):
    topChannels = getTopChannels()
    topChannels = instantiateJsonToClassObj(topChannels) # relevant_data = /mocks/initScrapData.py
    topChannels = addVipList(topChannels) # same ^ but with gera
    scrapped_channels = seleniumController.scrape4VidHref(topChannels, isDebug)

    if isEnd:
        print(json.dumps(scrapped_channels, default=lambda o: o.__dict__, indent=4))
        return json.dumps(scrapped_channels, default=lambda o: o.__dict__, indent=4)
    return scrapped_channels

def getTopChannels(*, isDebug=False): # Returns big json: { "data": [ { "avgviewers": 53611, "displayname": "xQc", ...
    print ("000000000000                         00000000000000000")
    print ("000000000000 getTopChannels - sully  00000000000000000")
    print ("000000000000                         00000000000000000")

    num_channels = int(env_varz.SULLY_NUM_CHANNELS)
    if num_channels > 300 or (num_channels % 10) != 0:
        raise Exception("Error, num_channels is too big or not in 10s: " + str(num_channels))
    pageSize = 100
    loopMax = max(1, int((num_channels / pageSize)))
    type = 3 # note '3' = most watched
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }
    accumilator = []
    complete_json = { "data": accumilator}
    for i in range(loopMax):
        startAt = (i * pageSize) 
        # url = 'https://sullygnome.com/api/tables/channeltables/getchannels/30/0/0/3/desc/0/100'
        url = (f'https://sullygnome.com/api/tables/channeltables/getchannels/14/0/{str(i)}/{type}/desc/{str(startAt)}/{str(pageSize)}')
        response = requests.get(url, headers=headers)
        print ("    (getTopChannels) ----------------------")
        print ("    " + url)
        print ("    (getTopChannels) ----------------------")
        print ('    (getTopChannels) reponse code = ' + str(response.status_code))
        # print ("response.text =" + response.text)
        if response.status_code >= 200 and response.status_code < 300:
            res_json = response.json()
            if 'data' in res_json:
                data = res_json['data']
                cnt = 0
                accumilator.extend(data)
                for obj in data:
                    print("    (getTopChannels) " + str(i) + " @ "+ str(cnt) + " --- " + str(obj.get('url')))
                    # print('    ' + str(obj))
                    # print('    (getTopChannels) url=' + str(obj.get('url')))
                    # print('    (getTopChannels) displayname=' + str(obj.get('displayname')))
                    # print('    (getTopChannels) language=' + str(obj.get('language')))
                    # print('    (getTopChannels) viewminutes=' + str(obj.get('viewminutes')))
                    # print('    (getTopChannels) logo=' + str(obj.get('logo')))
                    # print('    (getTopChannels) current_rank=' + str(obj.get('current_rank')))
                    cnt= cnt + 1
        else:
            print(f'Error: {response.status_code}')
    print ("    (getTopChannels) DONE!")
    # print (complete_json)
    return complete_json


def instantiateJsonToClassObj(json_object):
    relevant_list: List[ScrappedChannel] = []
    for channel in json_object['data']: 
        # print(channel)
        scrapped_channel = ScrappedChannel(
            displayname=channel.get('displayname'), 
            language=channel.get('language'), 
            logo=channel.get('logo'), 
            current_rank=channel.get('rownum'), 
            twitchurl=channel.get('twitchurl'), 
            name_id=channel.get('url')
        )
        relevant_list.append(scrapped_channel)
    return relevant_list

def addVipList(channels: List[ScrappedChannel]):
    VIP_LIST = [
        {
            "displayname": "LoLGeranimo",
            "language": "English",
            "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
            "twitchurl": "https://www.twitch.tv/lolgeranimo",
            "url": "lolgeranimo",
            "rownum": -2
        }
    ]
    if os.getenv("ENV") == "local":
        VIP_LIST.append({
            "displayname": "Nmplol",
            "language": "English",
            "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/e4d9bf96-311d-487a-b5eb-9f9a94e0f795-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
            "twitchurl": "https://www.twitch.tv/nmplol",
            "url": "nmplol",
            "rownum": -1
        })
    for vip in VIP_LIST:
        scrapped_channel = ScrappedChannel(displayname=vip.get("displayname"),
                                           language=vip.get("language"),
                                           logo=vip.get("logo"),
                                           twitchurl=vip.get("twitchurl"),
                                           name_id=vip.get("url"),
                                           current_rank=vip.get("rownum"))
        channels.insert(0,scrapped_channel)
    return channels


