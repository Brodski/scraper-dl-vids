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

#
# TODO -
#       1. 
#
#
#

access_token = None
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



def getApiThing(scrapped_channels_all: List[ScrappedChannel]):
    global access_token
    client_id = env_varz.TWITCH_CLIENT_ID

    ### CREATE THE HTTP REQUEST + QUERY STRING ###
    scrapped_channels_all = ['twitchdev', 'geranimo', 'Sanchez']

    max_twitch_query = 100

    every_single_user = []

    for i in range(0, len(scrapped_channels_all), max_twitch_query):

        ### SETUP AND EMPTY ##
        user_login_list_aux= []
        query_string = "?"

        # We can only query 100 users per request
        user_login_list_aux = scrapped_channels_all[i:i+max_twitch_query]
        for user_login in user_login_list_aux:
            query_string += f"login={user_login}&"

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
        users_aux = [
            {key: user[key] for key in ("id", "login", "display_name")}
            for user in user_json["data"]
        ]
        every_single_user = every_single_user + users_aux
        
    for user in every_single_user:
        for i, channel in enumerate(scrapped_channels_all):
            channel: ScrappedChannel = channel
            if channel.name_id == user["login"]:
                channel.twitch_num_id = user["id"]
                break
    return 


    logger.debug("User info:\n%s", json.dumps(user_json, indent=4))
    logger.debug("----------")
    logger.debug("----------")
    logger.debug("----------")
    for f in every_single_user:
        logger.debug(f)

def getVods(scrapped_channels: List[ScrappedChannel]):
    # "SELECT NameId FROM Channels WHERE NameId IN ('geranimo', 'evelone2004', 'theburntpeanut', 'zackrawrr', 'kato_junichi0817', 'hasanabi', 'hjune', 'ohnepixel', 'ramzes', 'sasavot', 'illojuan', 'caseoh_', 'eliasn97', 'dota2_paragon_ru', 'jynxzi', 'xqc', 'plaqueboymax', 'esl_dota2', 'starladder_cs_en', 'tfue', 'stableronaldo', 'k3soju')"
    # databasePreper.getNewChannelsNotInDb(scrapped_channels)
    # return
    everyChannel:List[ScrappedChannel] = []
    

    global access_token
    client_id = env_varz.TWITCH_CLIENT_ID
    CHANNELS_MAX = int(env_varz.PREP_NUM_CHANNELS)
    VODS_MAX = int(env_varz.PREP_NUM_VOD_PER_CHANNEL)
    
    # channel: ScrappedChannel = None

    
    max_twitch_query = 100

    every_single_user = []

    for i in range(0, len(scrapped_channels), max_twitch_query):
        ### SETUP AND EMPTY ##
        scrapped_channels_aux = []
        query_string = "?"

        # We can only query 100 users per request
        scrapped_channels_aux: List[ScrappedChannel] = scrapped_channels[i:i+max_twitch_query]

        for channel in scrapped_channels_aux: # up to 100
            query_string += f"user_id={channel.twich_num_id}&"

            videos_url = f'https://api.twitch.tv/helix/videos{query_string}'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Client-Id': client_id
            }
            logger.debug(f"user_url={videos_url}")

            user_response = requests.get(videos_url, headers=headers)

            ### EXTRACT INFO ###
            user_json = user_response.json()
            # users_aux = [
            #     {key: user[key] for key in ("id", "user_login", "user_name", "created_at", "thumbnail_url", "url")}
            #     for user in user_json["data"]
            # ]

            logger.debug("User info:\n%s", json.dumps(user_json, indent=4))

            channel.links = allHrefs[:VODS_MAX]