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
import datetime
# import controllers.scrapey as scrapey
# import mocks.initScrapData as mockz
# use selenium to render the page and then scrape it with beautiful soup. 
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-web-page-into-python
# import re
import boto3
import json

# gameplan:
# Once a day
# Get top 100 channels from third party website
    # process it slightly
# Upload to s3
# Get last ~10 days from s3
# Create a set combining all 10 days
    # Must be channels
# Get everyone of their new vids
# speach -> text
# 
# upload to s3
# channels/rankings/2023-4-14/

# aggregate/2023-04-01.json  --> { date: 2023-04-01, data: [lolgera, xqc, moistcritical] }
# aggregate/2023-04-02.json
# aggregate/2023-04-03.json
# ...
# scraped/lolgeranimo/2023-04-01.json ---> { date: 2023-04-01, data: [1771303, 186211, 2441993] }
# scraped/lolgeranimo/2023-04-02.json ---> { date: 2023-04-02, data: [1989833, 1771303, 186211, 2441993] }
# ...
# captions/lolgeranimo/1771303/metadata.json
# captions/lolgeranimo/1771303/1771303.svt
# captions/lolgeranimo/1771303/1771303.txt
# captions/lolgeranimo/1771303/1771303.csv
# captions/lolgeranimo/2441993/metadata.json
# captions/lolgeranimo/2441993/2441993.svt
# captions/lolgeranimo/2441993/2441993.txt
# captions/lolgeranimo/2441993/2441993.csv
# ...
options = Options()
# options.add_argument('--headless')
options.add_argument('--window-size=1550,1250') # width, height
browser = None

CURRENT_DATE_YMD = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

# key = (filename) under which the JSON object will be stored in the S3 bucket
S3_KEY_RANKING = "channels/ranking/" + CURRENT_DATE_YMD


BUCKET_NAME = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket'
directory_name = 'mydirectory' # this directory legit exists in this bucket ^
directory_name_real = "channels/ranking/raw" 

VIP_LIST = [
    {
        "displayname": "LoLGeranimo",
        "language": "English",
        "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
        "twitchurl": "https://www.twitch.tv/lolgeranimo",
        "url": "lolgeranimo"
    }
  ]


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

def getTopChannels(*, numChannels=50): # Returns big json: { "data": [ { "avgviewers": 53611, "displayname": "xQc", ...
    if numChannels > 300 or (numChannels % 10) != 0:
        print("Error, numChannels is too big: " + str(numChannels))
        return
    loopMax = int((numChannels / 10))
    # pageSize = 100
    pageSize = 10
    type = 3 # 3 = enum = Most watched
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
        print ("-------------------------------------------------------------------")
        print (url)
        print ("-------------------------------------------------------------------")

        response = requests.get(url, headers=headers)

        print ('reponse code = ' + str(response.status_code))
        print ('response.reason: ' + str(response.reason))
        print ('size: ' + str(len(response.content)))
        # print ("response.text =" + response.text)
        print ()
        if response.status_code >= 200 and response.status_code < 300:
            res_json = response.json()
            if 'data' in res_json:
                data = res_json['data']
                cnt = 0
                accumilator.extend(data)
                for obj in data:
                    print(str(i) + " @ "+ str(cnt) + ": =========================")
                    print(obj)
                    print('userId=' + str(obj.get('userId')))
                    print('language=' + str(obj.get('language')))
                    print('viewminutes=' + str(obj.get('viewminutes')))
                    print('displayname=' + str(obj.get('displayname')))
                    print('url=' + str(obj.get('url')))
                    print('logo=' + str(obj.get('logo')))
                    cnt= cnt + 1
        else:
            print(f'Error: {response.status_code}')
    print ("DONE!")
    # print (complete_json)
    return complete_json

# https://stackoverflow.com/questions/46844263/writing-json-to-file-in-s3-bucket
def saveTopChannels(json_data):
    if json_data is None:
        abort(400, description="Data is None - Nothing to save. Aborting save")
    try:
        s3 = boto3.client('s3')
        key = S3_KEY_RANKING + ".json" # channels/rankings/raw/2023-15/2.json
        
        s3.put_object(
            Body=json.dumps(json_data),
            Bucket=BUCKET_NAME,
            Key=key
        )
        # Successfully saved to: channels/ranking/2023-05-10.json
        print("Successfully saved this as a file: \n" + str(json_data))
        for channel in json_data['data']:
            print (channel['displayname'])
        print("Successfully saved to: " + key)
        print('---')
        return json_data
    except:
        abort(400, description="Something went wrong at saveTopChannels()")

def getChannelInS3AndTidy(sorted_s3_paths):
    s3 = boto3.client('s3')
    print("GETTING ALL CONTENT")
    relevant_list = []
    already_added_list = []
    for key in sorted_s3_paths:
        print(key)
        responseGetObj = s3.get_object(
            Bucket = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket',
            Key = key # ex) 'channels/ranking/2023-04-14.json'
        )
        binary_data = responseGetObj['Body'].read()
        json_string = binary_data.decode('utf-8')
        json_object = json.loads(json_string) # { "data":[ { "viewminutes":932768925, "streamedminutes":16245, ... } ] }

        llist = tidyData(json_object)
        for channel in llist:
            if channel.get('displayname') in already_added_list:
                continue
            already_added_list.append(channel.get('displayname'))
            relevant_list.append(channel)
    print ("WE DONE")
    for r in relevant_list:
        print (r['displayname'])
    print (len(relevant_list))
    print (len(relevant_list))
    print (len(relevant_list))
    return relevant_list

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

# Query the s3 with the formated json of top channels
def preGetChannelInS3AndTidy() -> List[str]:  
    # - Note boto3 returns last modified as: datetime.datetime(2023,4,10,7,44,12,"tzinfo=tzutc()
    # Thus
    #     obj['Key']          = channels/ranking/raw/2023-15/100.json = location of metadata
    #     obj['LastModified'] = Last modified: 2023-04-11 06:54:39+00:00

    
    # REACH_BACK_DAYS = Content / UX thing
    # Recall, our S3 saves top X channels every day, REACH will allow us to grab a couple more channels incase 
    # a channel begins to slip in ranking not b/c of popularity but b/c IRL stuff or w/e
    #
    REACH_BACK_DAYS = 5
    s3 = boto3.client('s3')
    # TODO env var this Prefix
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="channels/ranking/")['Contents']
    sorted_objects = sorted(objects, key=lambda obj: obj['LastModified'])
    print("-----SORTED (OFFICIAL)---- " + str(REACH_BACK_DAYS) + " days ago")
    keyPathList = []
    sorted_objects = sorted_objects[-REACH_BACK_DAYS:]
    for obj in sorted_objects:
        print("Key= " + f"{obj['Key']} ----- Last modified= {obj['LastModified']}")
        keyPathList.append(obj['Key'])

        
    return keyPathList


def addVipList(channels):
    for channel in VIP_LIST:
        channels.insert(0,channel)
    return channels
