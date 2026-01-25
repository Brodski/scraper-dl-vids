import argparse
import copy
import sys
import time
import traceback
from typing import List
import urllib.request
import urllib.parse
import json
import os
from urllib.parse import quote_plus  # Python 3+
import boto3
import os

import vast_api as vast_api
import print_extra as print_extra
from emailer_vast import sendEmail
from emailer_vast import MetadataVast
from Configz import configz
from Instance_V import Instance_V
from Instance_V import Status

#########################################################################
#                                                                       #
# Note: find_create_instance() is the "main()" Defined in lambda_vastai.tf    #
# Vars: vars_prod.tf locally on -> terraform -> lambda -> python        #  
#                                                                       #
#########################################################################

## INIT VARS ###
metadata_vast_global: MetadataVast = MetadataVast()
instance_v_global_list: List[Instance_V] = []
id_tracker_trick = {}
for i in range(configz.TRANSCRIBER_NUM_INSTANCES):
    id_tracker_trick[i] = False
bullshit_recursion_max = 20
bullshit_recursion_cnt = 0

def getOffers():
    goodOffers = []
    everything_request = '''{
            "q":{ 
                "verified": {"eq": true},
                "external": {"eq": false},
                "rentable": {"eq": true},
                "order":[[   "dph_total",   "asc"] ],
                "type":"on-demand"
                }
            }
        '''
    offers = vast_api.requestOffersHttp(json.loads(everything_request))
    for offer in offers:
        id = "id: " + str(offer.get("id"))
        if offer.get("cuda_max_good") < int(configz.cuda_vers):
            # print(id + " skipping cuda_max_good: " + str(offer.get("cuda_max_good")))
            continue
        if offer.get("dph_total") < float(configz.dph_min):
            continue
        if offer.get("dph_total") > float(configz.dph):
            # print(id + " skipping dph: " + str(offer.get("dph_total")))
            continue
        if offer.get("cpu_ram") < float(configz.cpu_ram):
            # print(id + " skipping cpu_ram: " + str(offer.get("cpu_ram")))
            continue
        if offer.get("disk_space") < float(configz.disk_space):
            # print(id + " skipping disk_space: " + str(offer.get("disk_space")))
            continue
        if offer.get("gpu_ram") < float(configz.gpu_ram):
            # print(id + " skipping gpu_ram: " + str(offer.get("gpu_ram")))
            continue
        if offer.get("storage_cost") > float(configz.storage_cost):
            # print(id + " skipping storage_cost: " + str(offer.get("storage_cost")))
            continue
        if offer.get("inet_down_cost") > float(configz.inet_down_cost):
            # print(id + " skipping inet_down_cost: " + str(offer.get("inet_down_cost")))
            continue
        if offer.get("inet_up_cost") > float(configz.inet_up_cost):
            # print(id + " skipping inet_up_cost: " + str(offer.get("inet_up_cost")))
            continue
        if offer.get("gpu_name") in configz.blacklist_gpus:
            # print(id + " skipping blacklist_gpus: " + str(offer.get("gpu_name")))
            continue
        if str(offer.get("id")) in configz.blacklist_ids:
            # print(id + " skipping blacklist_ids: " + str(offer.get("id")))
            continue
        # print("======================")
        # print("ADDING " + id)
        goodOffers.append(offer)
    
    goodOffers = sorted(goodOffers, key=lambda x: x['dph_total'])
    return goodOffers

def get_good_instance_num_smart():
    first_instance_not_created_trick = -1
    for k,v in id_tracker_trick.items():
        if v == False:
            first_instance_not_created_trick = k
            id_tracker_trick[k] = True
            break
    return first_instance_not_created_trick

def find_create_instance(rerun_count, to_create_num):
    ############################
    ###                      ###
    ### FIND VIABLE INSTANCE ###
    ###                      ###
    ############################
    print(f"  (find_create_xinstance) TOP rerun_count: {rerun_count}")
    if (rerun_count >= 3):
        print("  (find_create_xinstance) We have reran too many time,  ENDING!\n" * 3)
        return
    if to_create_num <= 0:
        return

    goodOffers = getOffers()
    
    if len(goodOffers) == 0:
        print("THERE ARE NO GOOD OFFERS!\n" * 9)
        print("Gonna try again in 4 min")
        time.sleep(120)
        print('2 min passed ...')
        time.sleep(120)
        print('4 min passed ...')
        find_create_instance(rerun_count + 1, to_create_num)
        return
    
    ##################################
    ##   INSTANTIATE VAST AI 'VM'   ##
    ##################################
    print_extra.printAsTable(goodOffers)
    instances_aux_list = goodOffers[:to_create_num] 
    # instance_v_created: List[Instance_V] = []

    for offer_i in instances_aux_list:
        instance_num = get_good_instance_num_smart()
        try:
            # instance_num          = len(instance_v_global_list)
            instance_num            = instance_num
            id_contract             = vast_api.create_instance(offer_i, instance_num)
            instance_v              = Instance_V()
            instance_v.id_contract  = id_contract
            instance_v.status       = None # explicit
            instance_v.time_created = time.time()
            instance_v.instance_num = instance_num

            instance_v_global_list.append(instance_v)
            time.sleep(60)

        except Exception as e:
            stacktrace_str = traceback.format_exc()
            print(f"   (find_create_xinstance) Trying again. Error creating instance {e}")
            print(stacktrace_str)

            metadata_vast_global.errorz.append({"rerun_count": rerun_count, "stacktrace_str": stacktrace_str})

            to_create_aux = to_create_num - len(instance_v_global_list)

            find_create_instance(rerun_count + 1, to_create_aux)
            return
    return
            


def pollxCompletion2():
    failed_list = []
    vast_data_dictionary = print_extra.get_all_instances(instance_v_global_list)
    for instance in instance_v_global_list:
        if instance.status in (Status.ERROR_1, Status.ERROR_2, Status.ERROR_3, Status.RUNNING, Status.RUNNING_FAST_EXIT):
            continue
        instance: Instance_V = instance
        status_msg          = None
        actual_status       = None
        exec_time_minutes   = instance.get_exec_time() # (time.time() - instance.time_created) / 60
        try:
            data            = vast_data_dictionary[instance.id_contract]
        except KeyError:
            instance.status = Status.RUNNING_FAST_EXIT
            # metadata_vast_global.successes.append({'id': instance.id_contract, "exec_time_minutes": exec_time_minutes, **dataX})
            metadata_vast_global.successes.append({'id': instance.id_contract, "exec_time_minutes": exec_time_minutes})
            continue
        # data                = getStatusVast(instance)
        status_msg : str    = data["status_msg"]
        actual_status : str = data["actual_status"]
        
        print(f"    (getStatusVast) ...polling id {instance.id_contract}'s actual_status: ", actual_status)
    
        if status_msg and status_msg.lower().startswith("unexpected fault address"):
            print("nope not ready, 'unexpected fault address' end it")
            instance.status = Status.ERROR_1
            failed_list.append({"instance": copy.copy(instance), "data": data, "exec_time_minutes": exec_time_minutes})
            continue
        if status_msg and "unable to find image" in status_msg.lower():
            print("nope not ready, end it")
            instance.status = Status.ERROR_2
            failed_list.append({"instance": copy.copy(instance), "data": data, "exec_time_minutes": exec_time_minutes})
            continue
        if actual_status and actual_status.lower() == "loading" and exec_time_minutes > 7: # 7 minutes. Image is stuck loading
            print(f"nope not ready and exec_time_minutes > 7 min, end it. exec_time_minutes: {exec_time_minutes}")
            instance.status = Status.ERROR_3
            failed_list.append({"instance": copy.copy(instance), "data": data, "exec_time_minutes": exec_time_minutes})
            continue
        if status_msg and status_msg.lower().startswith("Error response from daemon: failed to create task for container"):
            print("nope not ready, 'failed to create shim task: OCI runtime' end it")
            instance.status = Status.ERROR_4
            failed_list.append({"instance": copy.copy(instance), "data": data, "exec_time_minutes": exec_time_minutes})
            continue
        if actual_status and actual_status.lower() == "running":
            print("Running. Transcriber app should be running. :)")
            instance.status = Status.RUNNING
            dataX = nice_data(data)
            metadata_vast_global.successes.append({'id': instance.id_contract, "exec_time_minutes": exec_time_minutes, **dataX})
            continue
        instance.polling_count += 1
        instance.status = Status.LOADING
    # AFTER LOOP
    for fail in failed_list:
        instance           = fail["instance"]
        data               = fail["data"]
        exec_time_minutesX = fail["exec_time_minutes"]
        try_again(instance, data, exec_time_minutesX)
    
    return len(failed_list)



def getStatusVast(instance: Instance_V):
    print(f'----- Poll count: {instance.polling_count}: polling {str(instance.id_contract)} for completion -----')

    data = print_extra.get_my_instance_baby(instance.id_contract)
    return data

def nice_data(data):
    search = data.get("search", {}) #safety

    return {
        "cpu_name"                 : data.get("cpu_name"),
        "cpu_ram"                  : data.get("cpu_ram"),
        "cpu_cores"                : data.get("cpu_cores"),
        "gpu_name"                 : data.get("gpu_name"),
        "gpu_arch"                 : data.get("gpu_arch"),
        "gpu_totalram"             : data.get("gpu_totalram"),
        "gpuCostPerHour"           : search.get("gpuCostPerHour"),
        "internet_down_cost_per_tb": data.get("internet_down_cost_per_tb"),
        "internet_up_cost_per_tb"  : data.get("internet_up_cost_per_tb"),
        "min_bid"                  : data.get("min_bid"),
        "vram_costperhour"         : data.get("vram_costperhour"),
        "status_msg"               : data.get("status_msg"),
        "actual_status"            : data.get("actual_status"),
        "geolocation"              : data.get("geolocation"),
        "reliability"              : data.get("reliability"),
        "dph_total"                : data.get("dph_total"),
        "actual_status"            : data.get("actual_status"),
        "actual_status"            : data.get("actual_status"),
    }

def try_again(instance: Instance_V, data, exec_time_minutes):
    ### METADATA ###
    status_msg: str    = data["status_msg"]
    actual_status: str = data["actual_status"]
    status_msg_arr = [f"id: {instance.id_contract}. status_msg: {status_msg}. actual_status: {actual_status}"]
    dataX = nice_data(data)
    metadata_vast_global.try_again_arr.append({'id': instance.id_contract, 'status_msg_arr': status_msg_arr, 'exec_time_minutes': exec_time_minutes, **dataX })

    ### DELETE ###
    print("   ! (try_again) stopping bad instance")
    vast_api.destroy_instance(instance.id_contract)
    configz.blacklist_ids.append(str(instance.id_contract))

    idx = None
    for i, v in enumerate(instance_v_global_list):
        v: Instance_V = v
        if str(v.id_contract) == str(instance.id_contract):
            idx = i
            instance_v_global_list.pop(idx)
            id_tracker_trick[int(instance.instance_num)] = False # Make the key at instance_num available/False
            print(f"   ! (try_again) popping at {idx}")
            break


def goBabyGo(to_create_num):
    global bullshit_recursion_cnt
    bullshit_recursion_cnt += 1
    if bullshit_recursion_cnt > bullshit_recursion_max:
        print(" ❗our recursion might be funked up for some reason")
        metadata_vast_global.send_fail_msg()
        sys.exit(1)
    try:
        ############
        #  BOOM 1  #
        ############
        find_create_instance(0, to_create_num)

        if len(instance_v_global_list) < configz.TRANSCRIBER_NUM_INSTANCES:
            to_create_remaining = configz.TRANSCRIBER_NUM_INSTANCES - len(instance_v_global_list)
            time.sleep(10)      # Incase VastAI's api is slow/cached, i guess this might help
            goBabyGo(to_create_remaining)
            return              # Keep running goBabyGo() until all are completed

        ############
        #  BOOM 2  #
        ############
        num_failed = pollxCompletion2()
        if num_failed > 0:
            goBabyGo(num_failed)
            return 

        for instance in instance_v_global_list:
            if instance.status == Status.LOADING:
                print("Sleeping 60 sec, at least 1 instance still loading....")
                time.sleep(60)
                to_create_aux = 0
                goBabyGo(to_create_aux)
                return 
        metadata_vast_global.send_success_msg()
    except:
        tr = traceback.format_exc()
        metadata_vast_global.send_fail_msg(tr)

    return {
        'statusCode': 200,
        'body': json.dumps('Completed vastai init!! ')
    }
def handler_kickit(event, context):
    result = goBabyGo(configz.TRANSCRIBER_NUM_INSTANCES)
    global bullshit_recursion_cnt
    global instance_v_global_list
    global id_tracker_trick

    bullshit_recursion_cnt = 0
    instance_v_global_list = []
    id_tracker_trick = {}
    return result

if __name__ == '__main__':
    handler_kickit(None, None)
    