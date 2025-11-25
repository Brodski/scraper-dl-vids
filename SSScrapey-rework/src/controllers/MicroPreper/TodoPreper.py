from __future__ import unicode_literals
import math
from models.ScrappedChannel import ScrappedChannel
from typing import List, Tuple, Dict
import controllers.MicroPreper.seleniumPreper as seleniumPreper
# import env_file as env_varz
from env_file import env_varz
import json
import os
import requests
import time
import logging
from utils.logging_config import LoggerConfig

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()




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


def getTopChannelsSully(*, isDebug=False): # Returns big json: { "data": [ { "avgviewers": 53611, "displayname": "xQc", ...
    logger.info("000000000000                         00000000000000000")
    logger.info("000000000000  getTopChannelsSully    00000000000000000")
    logger.info("000000000000                         00000000000000000")

    pageSize = 100
    # num_todo =  int(env_varz.PREP_SELENIUM_NUM_VODS_PER)
    num_todo =  int(env_varz.NUM_VOD_PER_CHANNEL)
    loopMax = math.ceil(num_todo / pageSize)

    days = int(env_varz.PREP_SULLY_DAYS) # 14
    type = 3 # note '3' = most watched
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }
    accumilator = []
    complete_json = { "data": accumilator}
    for i in range(loopMax):
        startAt = (i * pageSize) 
        # url = 'https://sullygnome.com/api/tables/channeltables/getchannels/14/0/0/3/desc/0/100'
        url = (f'https://sullygnome.com/api/tables/channeltables/getchannels/{str(days)}/0/{str(i)}/{type}/desc/{str(startAt)}/{str(pageSize)}')
        logger.info("----------------------")
        logger.info("    " + url)
        response = requests.get(url, headers=headers)
        if response.status_code >= 200 and response.status_code < 300:
            res_json = response.json()
            if 'data' in res_json:
                data = res_json['data']
                cnt = 0
                accumilator.extend(data)
                for obj in data:
                    logger.debug(str(i) + " @ "+ str(cnt) + " --- " + str(obj.get('url')))
                    cnt= cnt + 1
                    # logger.debug('    ' + str(obj))
                    # logger.debug('    (getTopChannelsSully) url=' + str(obj.get('url')))
                    # logger.debug('    (getTopChannelsSully) displayname=' + str(obj.get('displayname')))
                    # logger.debug('    (getTopChannelsSully) language=' + str(obj.get('language')))
                    # logger.debug('    (getTopChannelsSully) viewminutes=' + str(obj.get('viewminutes')))
                    # logger.debug('    (getTopChannelsSully) logo=' + str(obj.get('logo')))
                    # logger.debug('    (getTopChannelsSully) current_rank=' + str(obj.get('current_rank')))
                    # logger.debug('     (getTopChannelsSully) viewminutes        ', obj.get('viewminutes'))
                    # logger.debug('     (getTopChannelsSully) streamedminutes    ', obj.get('streamedminutes'))
                    # logger.debug('     (getTopChannelsSully) maxviewers         ', obj.get('maxviewers'))
                    # logger.debug('     (getTopChannelsSully) avgviewers         ', obj.get('avgviewers'))
                    # logger.debug('     (getTopChannelsSully) rownum             ', obj.get('rownum'))
                    # logger.debug('     (getTopChannelsSully) followers          ', obj.get('followers'))
                    # logger.debug('     (getTopChannelsSully) followersgained    ', obj.get('followersgained'))
                    # logger.debug('     (getTopChannelsSully) partner            ', obj.get('partner'))
                    # logger.debug('     (getTopChannelsSully) affiliate          ', obj.get('affiliate'))
                    # logger.debug('     (getTopChannelsSully) mature             ', obj.get('mature'))
                    # logger.debug('     (getTopChannelsSully) language           ', obj.get('language'))
                    # logger.debug('     (getTopChannelsSully) previousviewminutes     ', obj.get('previousviewminutes'))
                    # logger.debug('     (getTopChannelsSully) previousstreamedminutes ', obj.get('previousstreamedminutes'))
                    # logger.debug('     (getTopChannelsSully) previousmaxviewers      ', obj.get('previousmaxviewers'))
                    # logger.debug('     (getTopChannelsSully) previousavgviewers      ', obj.get('previousavgviewers'))
                    # logger.debug('     (getTopChannelsSully) previousfollowergain    ', obj.get('previousfollowergain'))
                    # logger.debug('     (getTopChannelsSully) days    ', days)
        else:
            logger.debug(f'Error: {response.status_code}')
    logger.info("DONE!")
    # logger.debug(complete_json)
    return complete_json


def instantiateJsonToClassObj(json_object):
    relevant_list: List[ScrappedChannel] = []
    for channel in json_object['data']: 
        # logger.debug(channel)
        scrapped_channel = ScrappedChannel(
            displayname = channel.get('displayname'), 
            language = channel.get('language'), 
            logo = channel.get('logo'), 
            current_rank = channel.get('rownum'), 
            twitchurl = channel.get('twitchurl'), 
            name_id = channel.get('url'),
            viewminutes = channel.get('viewminutes'),
            streamedminutes = channel.get('streamedminutes'),
            maxviewers = channel.get('maxviewers'),
            avgviewers = channel.get('avgviewers'),
            followers = channel.get('followers'),
            followersgained = channel.get('followersgained'),
            partner = channel.get('partner'),
            affiliate = channel.get('affiliate'),
            mature = channel.get('mature'),
            previousviewminutes = channel.get('previousviewminutes'),
            previousstreamedminutes = channel.get('previousstreamedminutes'),
            previousmaxviewers = channel.get('previousmaxviewers'),
            previousavgviewers = channel.get('previousavgviewers'),
            previousfollowergain = channel.get('previousfollowergain')
        )
        relevant_list.append(scrapped_channel)
    return relevant_list

def addVipList(json_object, isDebug=False):
    import controllers.MicroPreper.seleniumPreper as seleniumPreper
    from controllers.MicroPreper.vip_list import vip_list, vip_list_debug

    VIP_LIST = []

    if os.getenv("ENV") == "local" or os.getenv("ENV") == "dev":
        VIP_LIST = VIP_LIST + [vip_list]

    if os.getenv("ENV") == "local" and isDebug:
        VIP_LIST = VIP_LIST + vip_list_debug  

    for vip in VIP_LIST:
        json_object['data'].insert(0, vip)
    return json_object

    #     scrapped_channel = ScrappedChannel(
    #         displayname=vip.get("displayname"),
    #         language=vip.get("language"),
    #         logo=vip.get("logo"),
    #         twitchurl=vip.get("twitchurl"),
    #         name_id=vip.get("url"),
    #         current_rank=vip.get("rownum"),
    #         viewminutes=vip.get("viewminutes"),
    #         streamedminutes=vip.get("streamedminutes"),
    #         maxviewers=vip.get("maxviewers"),
    #         avgviewers=vip.get("avgviewers"),
    #         followers=vip.get("followers"),
    #         followersgained=vip.get("followersgained"),
    #         partner=vip.get("partner"),
    #         affiliate=vip.get("affiliate"),
    #         mature=vip.get("mature"),
    #         previousviewminutes=vip.get("previousviewminutes"),
    #         previousstreamedminutes=vip.get("previousstreamedminutes"),
    #         previousmaxviewers=vip.get("previousmaxviewers"),
    #         previousavgviewers=vip.get("previousavgviewers"),
    #         previousfollowergain=vip.get("previousfollowergain")
    #     )
    #     channels.insert(0,scrapped_channel)
    # return channels
