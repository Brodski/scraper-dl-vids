import argparse
import time
import traceback
import urllib.request
import urllib.parse
import json
import os
from urllib.parse import quote_plus  # Python 3+
import boto3
import os

from configz import *
import vast_api as vast_api
import print_extra as print_extra
from emailer_vast import sendEmail
from emailer_vast import MetadataVast

# import sys
# target = os.path.abspath("../src/utils/")
# sys.path.insert(0, target)

#########################################################################
#                                                                       #
# Note: find_create_confirm_instance() is the "main()" Defined in lambda_vastai.tf    #
# Vars: vars_prod.tf locally on -> terraform -> lambda -> python        #  
#                                                                       #
#########################################################################

metadata_vast: MetadataVast = MetadataVast()

def find_create_confirm_instance(rerun_count, instance_num):
    ############################
    ###                      ###
    ### FIND VIABLE INSTANCE ###
    ###                      ###
    ############################
    print(f"  (find_create_confirm_instance) TOP rerun_count: {rerun_count}, instance_num: {instance_num}")
    if (rerun_count >= 2):
        print("  (find_create_confirm_instance) We have reran too many time,  ENDING!\n" * 3)
        return

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
    goodOffers = []
    for offer in offers:
        id = "id: " + str(offer.get("id"))
        if offer.get("cuda_max_good") < int(cuda_vers):
            # print(id + " skipping cuda_max_good: " + str(offer.get("cuda_max_good")))
            continue
        if offer.get("dph_total") > float(dph):
            # print(id + " skipping dph: " + str(offer.get("dph_total")))
            continue
        if offer.get("cpu_ram") < float(cpu_ram):
            # print(id + " skipping cpu_ram: " + str(offer.get("cpu_ram")))
            continue
        if offer.get("disk_space") < float(disk_space):
            # print(id + " skipping disk_space: " + str(offer.get("disk_space")))
            continue
        if offer.get("gpu_ram") < float(gpu_ram):
            # print(id + " skipping gpu_ram: " + str(offer.get("gpu_ram")))
            continue
        if offer.get("storage_cost") > float(storage_cost):
            # print(id + " skipping storage_cost: " + str(offer.get("storage_cost")))
            continue
        if offer.get("inet_down_cost") > float(inet_down_cost):
            # print(id + " skipping inet_down_cost: " + str(offer.get("inet_down_cost")))
            continue
        if offer.get("inet_up_cost") > float(inet_up_cost):
            # print(id + " skipping inet_up_cost: " + str(offer.get("inet_up_cost")))
            continue
        if offer.get("gpu_name") in blacklist_gpus:
            # print(id + " skipping blacklist_gpus: " + str(offer.get("gpu_name")))
            continue
        if str(offer.get("id")) in blacklist_ids:
            # print(id + " skipping blacklist_ids: " + str(offer.get("id")))
            continue
        # print("======================")
        # print("ADDING " + id)
        goodOffers.append(offer)
    
    goodOffers = sorted(goodOffers, key=lambda x: x['dph_total'])

    if len(goodOffers) == 0:
        print("THERE ARE NO GOOD OFFERS!\n" * 9)
        print("Gonna try again in 5 min")
        time.sleep(150)
        print('2.5 min passed ...')
        time.sleep(150)
        print('5 min passed ...')
        find_create_confirm_instance(rerun_count + 1, instance_num)
        return
    

    ##################################
    ####                          ####
    #### INSTANTIATE VAST AI 'VM' ####
    ####                          ####
    ##################################
    print_extra.printAsTable(goodOffers)
    instance_first = goodOffers[0]

    try:
        id_create   = instance_first.get("id")
        ## BOOM 1 ##
        id_contract = vast_api.create_instance(id_create, instance_num)
        ## BOOM 2 ##
        status      = pollCompletion(id_contract, time.time(), 0, instance_num)
        if status == "success":
            pass
            # WE PRINT A LOT OF INFO
            # print_extra.printDebug(id_contract)
        else:
            print("  (find_create_confirm_instance) POLL FAILED. id:", id_contract, " - STATUS:", status)
            vast_api.destroy_instance(id_contract)
    except Exception as e:
        traceback.print_exc()
        stacktrace_str = traceback.format_exc()
        print(f"   (find_create_confirm_instance) Trying agian. Error creating instacne {e}")
        metadata_vast.errorz.append({"rerun_count": rerun_count, "stacktrace_str": stacktrace_str})
        find_create_confirm_instance(rerun_count + 1, instance_num)
            
    return {
        'statusCode': 200,
        'body': json.dumps('Completed vastai init!! ')
    }

def pollCompletion(id_contract, start_time, counter_try_again, instance_num, status_msg_arr = []):
    print(f'----- {counter_try_again}: polling {str(id_contract)} for completion -----')

    if counter_try_again > 11: # 11 min
        print(f"    (pollCompletion) Ending! counter_try_again > 11. counter_try_again={counter_try_again}")
        return
    status_msg          = None
    actual_status       = None
    exec_time_minutes   = (time.time() - start_time) / 60
    id_contract         = str(id_contract)
    # rows                = print_extra.get_my_instances()
    data                = print_extra.get_my_instance_baby(id_contract)
    status_msg : str    = data["status_msg"]
    actual_status : str = data["actual_status"]
    
    print(f"    (pollCompletion) ...polling... {id_contract}'s actual_status: ", actual_status)
    # "actual_status": "running",
    # "status_msg": "success, running cbrodski/transcriber:official_v2_dev",
 
    status_msg_arr.append(f"status_msg: {status_msg}. actual_status: {actual_status}")


    if status_msg and status_msg.lower().startswith("unexpected fault address"):
        print("    (pollCompletion) nope not ready, 'unexpected fault address' end it")
        try_again(id_contract, instance_num, data, status_msg_arr, exec_time_minutes)
        return
    if status_msg and "unable to find image" in status_msg.lower():
        print("    (pollCompletion) nope not ready, end it")
        try_again(id_contract, instance_num, data, status_msg_arr, exec_time_minutes)
        return
    if actual_status and actual_status.lower() == "loading" and exec_time_minutes > 7: # 7 minutes. Image is stuck loading
        print("    (pollCompletion) nope not ready and exec_time_minutes > 7 min, end it. exec_time_minutes:", exec_time_minutes)
        try_again(id_contract, instance_num, data, status_msg_arr, exec_time_minutes)
        return
    if actual_status and actual_status.lower() == "running":
        print("    (pollCompletion) Running. Transcriber app should be running. :)")
        dataX = nice_data(data)
        metadata_vast.successes.append({'id': id_contract, "exec_time_minutes": exec_time_minutes, **dataX})
        return "success"
    time.sleep(60) 
    return pollCompletion(id_contract, start_time, counter_try_again+1, instance_num)

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

def try_again(id, instance_num, data, status_msg_arr, exec_time_minutes):
    ### METADATA ###
    dataX = nice_data(data)
    metadata_vast.try_again_arr.append({'id': id, 'status_msg_arr': status_msg_arr, 'exec_time_minutes': exec_time_minutes, **dataX })

    ### DELETE ###
    print("   ! (try_again) stopping bad instance")
    vast_api.destroy_instance(id)
    blacklist_ids.append(id)

    ### RETRY ###
    print("   ! (try_again) creating a new instance ...")
    find_create_confirm_instance(0, instance_num)


def handler_kickit(event, context):
    try:
        num_instances = 1 if TRANSCRIBER_NUM_INSTANCES is None else int(TRANSCRIBER_NUM_INSTANCES)
        for i in range(num_instances):
            print(f" -------------- {i} --------------")
            print(f" ------- instance # {str(i + 1)} of {TRANSCRIBER_NUM_INSTANCES} -------")
            print(f" --------------   --------------")
            find_create_confirm_instance(0, i)
            time.sleep(10) # I dont remember why i put this
        metadata_vast.send_success_msg()
    except:
        tr = traceback.format_exc()
        metadata_vast.send_fail_msg(tr)
        # env = os.getenv("ENV")
        # subject = f"Vast-master/lambda {env} FAILED"
        # body = tr
        # sendEmail(subject, body)
        # mes

if __name__ == '__main__':
    handler_kickit(None, None)
    