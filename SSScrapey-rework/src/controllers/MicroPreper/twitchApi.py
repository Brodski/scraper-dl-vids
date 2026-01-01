from typing import List
import requests
from env_file import env_varz
import json
import os
import requests
import logging
from utils.logging_config import LoggerConfig
import json
from models.ScrappedChannel import ScrappedChannel
import controllers.MicroPreper.databasePreper as databasePreper

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()

access_token = None



def updateVidHref(scrapped_channels: List[ScrappedChannel]) -> List[ScrappedChannel]:
    if access_token == None: # we are in lambda, 15 min timeout < access_token's timeout
        initAccessToken()
    getTwitchIdAll(scrapped_channels)
    getVods(scrapped_channels)
    return scrapped_channels

def initAccessToken():
    client_id = env_varz.TWITCH_CLIENT_ID
    client_secret = env_varz.TWITCH_CLIENT_SECRET
    global access_token

    ### GET TOKEN ###
    token_url = 'https://id.twitch.tv/oauth2/token'
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json['access_token']   



def getTwitchIdAll(scrapped_channels_all: List[ScrappedChannel]):
    global access_token
    client_id = env_varz.TWITCH_CLIENT_ID

    ### CREATE THE HTTP REQUEST + QUERY STRING ###
    # scrapped_channels_all = ['twitchdev', 'geranimo', 'Sanchez']

    MAX_TWITCH_QUERY = 100

    json_all_batches = []

    for i in range(0, len(scrapped_channels_all), MAX_TWITCH_QUERY):

        ### SETUP AND EMPTY ##
        query_string = "?"

        # We can only query 100 users per request
        scrapped_channels_batch100: List[ScrappedChannel] = scrapped_channels_all[i:i+MAX_TWITCH_QUERY]
        for chann in scrapped_channels_batch100:
            query_string += f"login={chann.name_id}&"

        ### SEND REQUEST ###
        user_url = f'https://api.twitch.tv/helix/users{query_string}'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Client-Id': client_id
        }
        logger.debug(f"user_url={user_url}")
        user_response = requests.get(user_url, headers=headers)

        ### EXTRACT INFO ###
        user_json = user_response.json()
        # users_aux = [ { "id": 12345, "login": geranimo, "display_name": Geranimo }, {}, {}, ... ]
        users_aux = [
            {key: user[key] for key in ("id", "login", "display_name")}
            for user in user_json["data"]
        ]
        json_all_batches = json_all_batches + users_aux
        
    ### ADD THE twitch_num_id TO EACH ScrappedChannel OBJECT ###
    ### (this is an inefficent loop) ###
    for user in json_all_batches:
        for i, channel in enumerate(scrapped_channels_all):
            channel: ScrappedChannel = channel
            if channel.name_id == user["login"]:
                logger.debug(f"Twitch id: {user['id']} --- Channel: {channel.name_id}")
                channel.twitch_num_id = user["id"]
                break
    return



def getVods(scrapped_channels: List[ScrappedChannel]):
    global access_token
    client_id = env_varz.TWITCH_CLIENT_ID
    CHANNELS_MAX = int(env_varz.PREP_NUM_CHANNELS)
    VODS_MAX = int(env_varz.PREP_NUM_VOD_PER_CHANNEL)

    ### QUERY STRING ###
    for channel in scrapped_channels: # up to 100
        channel: ScrappedChannel = channel
        if channel.twitch_num_id == None or channel.twitch_num_id == "None" or channel.twitch_num_id == "":
            logger.debug(f"Skipping {channel.name_id}. twitch_num_id is None for some reason")
            continue

        query_string = f"user_id={channel.twitch_num_id}"

        api_videos_url = f'https://api.twitch.tv/helix/videos?type=archive&sort=time&first={VODS_MAX}&{query_string}'
        headers = {'Authorization': f'Bearer {access_token}', 'Client-Id': client_id }

        logger.debug(f"api_videos_url={api_videos_url}")
        user_response = requests.get(api_videos_url, headers=headers)

        ### EXTRACT INFO ###
        user_json = user_response.json()
        # users_aux = [
        #     {key: user[key] for key in ("id", "user_login", "user_name", "created_at", "thumbnail_url", "url")}
        #     for user in user_json["data"]
        # ]
        # logger.debug("User info:\n%s", json.dumps(user_json, indent=4))
        # logger.debug("------------------------")

        for u_json in user_json["data"]:
            channel.links.append(u_json["id"])    
        logger.debug(f"channel.links={channel.links}")
        logger.debug("---")

        # channel.links = allHrefs[:VODS_MAX]