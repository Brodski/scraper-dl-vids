from __future__ import unicode_literals

import time
import asyncio
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from flask import jsonify
import requests
import datetime
import mocks
# use selenium to render the page and then scrape it with beautiful soup. 
# https://stackoverflow.com/questions/6028000/how-to-read-a-static-web-page-into-python
import re
import boto3
import json

options = Options()
# options.add_argument('--headless')
# key = (filename) under which the JSON object will be stored in the S3 bucket
# channels/rankings/raw/2023-<week#>/<i>
# channels/rankings/raw/2023-14/1.json
# channels/rankings/raw/2023-14/2.json
# channels/rankings/raw/2023-14/3.json
# channels/rankings/raw/2023-15/1.json
# channels/rankings/raw/2023-15/2.json
# ...
current_week = str(datetime.date.today().isocalendar()[1])
current_year = str(datetime.date.today().isocalendar()[0])
s3_key_base = "channels/ranking/raw/" + current_year + "-" + current_week + "/"
# The key (filename) under which the JSON object will be stored in the S3 bucket
s3_key = 'example.json'

options.add_argument('--window-size=1550,1250') # width, height
browser = None
channel = "lolgeranimo"

bucket_name = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket'
directory_name = 'mydirectory' # this directory legit exists in this bucket ^
directory_name_real = "channels/ranking/raw" 



def getAllS3Jsons():
    # "LastModified": datetime.datetime(2023,4,10,7,44,12,"tzinfo=tzutc()
    # obj['Key']          = channels/ranking/raw/2023-15/100.json
    # obj['LastModified'] = Last modified: 2023-04-11 06:54:39+00:00
    s3 = boto3.client('s3')
    objList = []
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=directory_name_real)['Contents']

    for obj in objects:
        objList.append(obj)
    sorted_objects = sorted(objList, key=lambda obj: obj['LastModified'])
    print ("objList")
    print ("objList")
    print (objList)
    print("-----SORTED----")
    for obj in sorted_objects:
        print(f"{obj['Key']} - Last modified: {obj['LastModified']}")

        
    x = datetime.datetime(2023, 4, 11, 6, 54, 39, 0, tzinfo=datetime.timezone.utc)
    filtered_objects = filter(lambda obj: obj['LastModified'] > x, sorted_objects)
    print("-----FILTER ----")
    print (x)
    for obj in filtered_objects:
        print(f"{obj['Key']} - Last modified: {obj['LastModified']}")
        
    return objects


# https://stackoverflow.com/questions/46844263/writing-json-to-file-in-s3-bucket
def uploadJsonToS3(json_data, count):
    s3 = boto3.client('s3')
    key = s3_key_base + str(count) + ".json" # channels/rankings/raw/2023-15/2.json
    print("saving: " + key)
    s3.put_object(
        Body=json.dumps(json_data),
        Bucket=bucket_name,
        Key=key
    )
    return "done: \n" + str(json_data)
    

def uploadChannelsJsonToS3():
    # loopMax = 15
    loopMax = 15
    pageSize = 100
    type = 3 # 3 = Most watched = net society time watching .... 3 = average viewers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }
    urls = []
    for i in range(loopMax):
        print (f"https://jsonplaceholder.typicode.com/posts/{i}")
        url = (f"https://jsonplaceholder.typicode.com/posts/{i}")
        startAt = (i * pageSize)
        # url = "https://jsonplaceholder.typicode.com/todos"
        # url = 'https://sullygnome.com/api/tables/channeltables/getchannels/30/0/0/3/desc/0/100'
        # print (f'https://sullygnome.com/api/tables/channeltables/getchannels/30/0/{str(i)}/{type}/desc/{str(startAt)}/{str(pageSize)}')
        # url = (f'https://sullygnome.com/api/tables/channeltables/getchannels/30/0/{str(i)}/{type}/desc/{str(startAt)}/{str(pageSize)}')

        response = requests.get(url, headers=headers)

        print ('reponse code = ' + str(response.status_code))
        print (response)
        # print ('headers')
        # print (response.headers)
        print ('reason:')
        print (response.reason)
        print ('size:')
        print (len(response.content))
        # print (response.text)
        if response.status_code >= 200 and response.status_code < 300:
            json_data = response.json()
            print("userId, id, title:")
            print(json_data.get("userId"))
            print(json_data.get("id"))
            print(json_data.get("title"))
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("UPLOADING TO S3 MUST UPDATE AT SOME POINT!!!!!!!!")
            uploadJsonToS3(json_data, startAt)
            if 'data' in json_data:
                data = json_data['data']
                for obj in data:
                    print("=========================")
                    print(obj)
                    print(obj.get('userId'))
                    print(obj.get('language'))
                    print(obj.get('viewminutes'))
                    print(obj.get('displayname'))
                    print(obj.get('url'))
                    print(obj.get('logo'))
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
    ### return await scrapePageGogo(channel)
    # loop = asyncio.new_event_loop()
    # loop.run_until_complete(gera())
    # loop.close()
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
    allHrefs = []
    for tag in vids:
        allHrefs.append(tag['href'])
        print ("tag['href']=" + tag['href'])
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



    
def uploadJsonToS3Test():
    s3 = boto3.client('s3')
    myJsonStff = { 
        "someArry": [
            { 
                "hello": "hello dude",
                "goodbye": "get out of here"
            },
            { 
                "party": "party hard",
                "gottaRock": "I wanna rock n roll",
                "gottaRock2": "I wanna rock n roll all night!"
            }
        ],
        "bangbang": "Pop boom bang! ka bam!"
    }
    json_object = myJsonStff
    s3.put_object(
        Body=json.dumps(json_object),
        Bucket=bucket_name,
        Key= s3_key_base + str(0) + ".json" # channels/rankings/raw/2023-15/2.json
        # Key=s3_key
    )
    return "done: \n" + str(myJsonStff)

def doS3Stuff():
    s3Aws = os.environ.get('BUCKET_NAME')
    s3local = os.environ.get('BUCKET_NAME_LOCAL')
    print(f'AWS_BUCKET Key: {s3Aws}')
    print(f'BUCKET_NAME_LOCAL Key: {s3local}')

    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=directory_name)['Contents']

    for obj in objects:
        print(obj['Key'])
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=directory_name) 
    print (response)
    print('================')
    print('================')
    print('================')
    print('================')
    for content in response.get('Contents', []):
        object_key = content.get('Key')
        print (object_key)
        # local_file_path = 'local/path/to/save/' + object_key.split('/')[-1]
        # s3.download_file(bucket_name, object_key, local_file_path)
    print('================')
    responseGetObj = s3.get_object(
            Bucket = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket',
            # Key = 'mydirectory/twitch-stuff.json'
            Key = 'mydirectory/testiq.png'
        )
    dataz = responseGetObj['Body'].read()
    print("len(dataz)=" + str(len(dataz)))
    return s3local

def testGetTop500Channels_NameCompleted():
    json_files = ['./mocks/0to100channels.json', './mocks/100to200channels.json']

    # Read and parse JSON files
    json_data = []
    for json_file in json_files:
        with open(json_file, 'r', encoding="utf8") as file:
            data = json.load(file)
            print(f"Contents length of file data = {len(data.get('data'))}:")
        print(data.get('thisdoesnotexist'))
        json_data.extend(data.get('data'))
        # print(f"Contents of {json_file}:")
        # print(data)
    print (';;;;;;;;;;;;;;;;;;')
    print (';;;;;;;;;;;;;;;;;;')
    print (';;;;;;;;;;;;;;;;;;')
    for dude in json_data:
        print (dude.get("displayname"))
    # gameplan:
    # Once a day
    # Get top 1500 channels from third party
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
    return json_data
