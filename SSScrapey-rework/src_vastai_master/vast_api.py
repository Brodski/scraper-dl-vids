
# copied from vast ai github https://github.com/vast-ai/vast-python/blob/d379d81c420f0f450b5759e3517d68ad89e1c39d/vast.py#L195
# copied from vast ai github https://github.com/vast-ai/vast-python/blob/d379d81c420f0f450b5759e3517d68ad89e1c39d/vast.py#L195
# copied from vast ai github https://github.com/vast-ai/vast-python/blob/d379d81c420f0f450b5759e3517d68ad89e1c39d/vast.py#L195
# copied from vast ai github https://github.com/vast-ai/vast-python/blob/d379d81c420f0f450b5759e3517d68ad89e1c39d/vast.py#L195
import argparse
import time
import traceback
import urllib.request
import urllib.parse
import json
import os
from urllib.parse import quote_plus  # Python 3+
from configz import *
from emailer_vast import MetadataVast

metadata_vast: MetadataVast = MetadataVast()

def requestOffersHttp(query_args):
    query_args["api_key"] = VAST_API_KEY
    query_json = "&".join("{x}={y}".format(x=x, y=quote_plus(y if isinstance(y, str) else json.dumps(y))) for x, y in query_args.items())
    # https://console.vast.ai/api/v0/bundles?q=%7B%22verified%22%3A+%7B%22eq%22%3A+true%7D%2C+%22external%22%3A+%7B%22eq%22%3A+false%7D%2C+%22rentable%22%3A+%7B%22eq%22%3A+true%7D%2C+%22dph%22%3A+%7B%22lt%22%3A+%220.12%22%7D%2C+%22dph_total%22%3A+%7B%22lt%22%3A+%220.12%22%7D%2C+%22cuda_vers%22%3A+%7B%22gte%22%3A+%2212%22%7D%2C+%22cuda_max_good%22%3A+%7B%22gte%22%3A+%2212%22%7D%2C+%22cpu_ram%22%3A+%7B%22gt%22%3A+16000.0%7D%2C+%22order%22%3A+%5B%5B%22cpu_ram%22%2C+%22asc%22%5D%5D%2C+%22type%22%3A+%22on-demand%22%7D&api_key=999999999999999999
    theRequest = "https://console.vast.ai/api/v0/bundles?" + query_json 
    url = theRequest
    response = urllib.request.urlopen(url)
    if response.status != 200:
        print('exiting, status not 200')
        exit()
    data = response.read()
    json_data = json.loads(data)
    return json_data.get("offers")

def create_instance(instance_id, instance_num):
    url = "https://console.vast.ai/api/v0/asks/" + str(instance_id) + "/?api_key=" + VAST_API_KEY
    data_dict =  {  
        "client_id": "me",
        "image": image, 
        "env": {'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY, 
                'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID,
                'ENV': ENV,
                'DATABASE_HOST': DATABASE_HOST,
                'DATABASE_USERNAME': DATABASE_USERNAME,
                'DATABASE_PASSWORD': DATABASE_PASSWORD,
                'DATABASE_PORT': DATABASE_PORT,
                'DATABASE': DATABASE,
                'VAST_API_KEY': VAST_API_KEY,
                'TRANSCRIBER_NUM_INSTANCES': TRANSCRIBER_NUM_INSTANCES,
                'TRANSCRIBER_VODS_PER_INSTANCE': TRANSCRIBER_VODS_PER_INSTANCE,
                'TRANSCRIBER_INSTANCE_CNT': (instance_num + 1),
            },
        "price": None, 
        "disk": disk, 
        "label": None, 
        "extra": None, 
        "onstart": None, 
        # "runtype": "ssh", 
        "runtype": "args", 
        "image_login": None, 
        "python_utf8": False, 
        "lang_utf8": False, 
        "use_jupyter_lab": False, 
        "jupyter_dir": None, 
        "create_from": None, 
        "force": False
        }
    data_json = json.dumps(data_dict).encode('utf-8')
    # if os.environ.get('ENV') == None or os.environ.get('ENV') == "local":
    #     print("ending early b/c local\n" *9)
    #     exit(0)
    request = urllib.request.Request(url, data=data_json, method='PUT')

    id = None
    with urllib.request.urlopen(request) as response:
        response_data = response.read()
        res_json = json.loads(response_data.decode('utf-8'))
        ### THE RESPONE DATA IS VERY SMALL  = {new_contract: 123, <1 other field>}##
        print(    "(create_instance) res_json: ", res_json)
        id = res_json.get("new_contract")

        ### METADATA ###
        metadata_vast.created.append({'id': id, 'status_code': str(response.status)})
    print(    "(create_instance) Created new instance:", id)
    return id


def destroy_instance(id):
    print("Destryoing instance: " + str(id))
    url = "https://console.vast.ai/api/v0/instances/" + str(id) + "/?api_key=" + VAST_API_KEY
    data_dict = {}
    data_json = json.dumps(data_dict).encode('utf-8')

    request = urllib.request.Request(url, data=data_json, method='DELETE')
    with urllib.request.urlopen(request) as response:
        response_data = response.read()
        status_code   = response.getcode()
        print(response_data.decode('utf-8'))
        print("delete's status_code " + str(status_code))

        ### METADATA ###
        metadata_vast.deleted.append({'id': id, 'status_code': status_code})
    print("DONE :)")

