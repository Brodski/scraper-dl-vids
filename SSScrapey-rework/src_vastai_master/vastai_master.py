import argparse
import time
import traceback
import urllib.request
import urllib.parse
import json
import os
from urllib.parse import quote_plus  # Python 3+


from configz import *
import vast_api as vast_api
import print_extra as print_extra

#########################################################################
#                                                                       #
# Note: find_create_confirm_instance() is the "main()" Defined in lambda_vastai.tf    #
# Vars: vars_prod.tf locally on -> terraform -> lambda -> python        #  
#                                                                       #
#########################################################################

        
def find_create_confirm_instance(rerun_count, instance_num):
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
            print(id + " skipping cuda_max_good: " + str(offer.get("cuda_max_good")))
            continue
        if offer.get("dph_total") > float(dph):
            print(id + " skipping dph: " + str(offer.get("dph_total")))
            continue
        if offer.get("cpu_ram") < float(cpu_ram):
            print(id + " skipping cpu_ram: " + str(offer.get("cpu_ram")))
            continue
        if offer.get("disk_space") < float(disk_space):
            print(id + " skipping disk_space: " + str(offer.get("disk_space")))
            continue
        if offer.get("gpu_ram") < float(gpu_ram):
            print(id + " skipping gpu_ram: " + str(offer.get("gpu_ram")))
            continue
        if offer.get("storage_cost") > float(storage_cost):
            print(id + " skipping storage_cost: " + str(offer.get("storage_cost")))
            continue
        if offer.get("inet_down_cost") > float(inet_down_cost):
            print(id + " skipping inet_down_cost: " + str(offer.get("inet_down_cost")))
            continue
        if offer.get("inet_up_cost") > float(inet_up_cost):
            print(id + " skipping inet_up_cost: " + str(offer.get("inet_up_cost")))
            continue
        if offer.get("gpu_name") in blacklist_gpus:
            print(id + " skipping blacklist_gpus: " + str(offer.get("gpu_name")))
            continue
        if str(offer.get("id")) in blacklist_ids:
            print(id + " skipping blacklist_ids: " + str(offer.get("id")))
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
    # print("  (find_create_confirm_instance)  Good offers: ")
    # print_extra.printAsTable(goodOffers)

    instance_first = goodOffers[0]
    # if create_auto or os.environ.get("IS_VASTAI_CREATE_INSTANCE") == "true": # env set in lambda_vastai.tf
    # exit(0)
    try:
        id_create = instance_first.get("id")
        id_contract = vast_api.create_instance(id_create, instance_num)
        status = pollCompletion(id_contract, time.time(), 0, instance_num)
        if status == "success":
            pass
            # WE PRINT A LOT OF INFO]
            # print("Status == 'success' Ya! :D", id_contract)
            # print_extra.printDebug(id_contract)
        else:
            print("  (find_create_confirm_instance) POLL FAILED. id:", id_contract, " - STATUS:", status)
            vast_api.destroy_instance(id_contract)
    except Exception as e:
        traceback.print_exc()
        print(f"   (find_create_confirm_instance) Trying agian. Error creating instacne {e}")
        find_create_confirm_instance(rerun_count + 1, instance_num)
            
    return {
        'statusCode': 200,
        'body': json.dumps('Completed vastai init!! ')
    }

def pollCompletion(id_contract, start_time, counter_try_again, instance_num):
    print(f'----- {counter_try_again}: polling {str(id_contract)} for completion -----')
    if counter_try_again > 11: # 11 min
        print(f"    (pollCompletion) Ending! counter_try_again > 11. counter_try_again={counter_try_again}")
        return
    status_msg = None
    actual_status = None
    exec_time_minutes = (time.time() - start_time) / 60
    id_contract = str(id_contract)
    rows = print_extra.get_my_instances()
    # get "status's" of our instance
    for row in rows:
        row_id = str(row['id'])
        if row_id == id_contract:
            print(f"    (pollCompletion) {row_id}'s actual_status: ", row.get("actual_status"))
            status_msg = row["status_msg"]
            actual_status = row["actual_status"]
            break
    
    if status_msg and status_msg.lower().startswith("unexpected fault address"):
        print("    (pollCompletion) nope not ready, 'unexpected fault address' end it")
        try_again(str(row['id']), instance_num)
        return
    if status_msg and "unable to find image" in status_msg.lower():
        print("    (pollCompletion) nope not ready, end it")
        try_again(str(row['id']), instance_num)
        return
    if actual_status and actual_status == "loading" and exec_time_minutes > 7: # 7 minutes. Image is stuck loading
        print("    (pollCompletion) nope not ready and exec_time_minutes > 7 min, end it. exec_time_minutes:", exec_time_minutes)
        try_again(str(row['id']), instance_num)
        return
    if actual_status and actual_status == "running":
        print("    (pollCompletion) Running. Transcriber app should be running. :)")
        return "success"
    # print('    (pollCompletion) sleeping for 60 sec')
    time.sleep(60) 
    return pollCompletion(id_contract, start_time, counter_try_again+1, instance_num)

def try_again(id, instance_num):
    print("   ! (try_again) end it")
    vast_api.destroy_instance(id)
    blacklist_ids.append(id)
    print("   ! (try_again) Try again")
    print("   ! (try_again) Try again")
    print("   ! (try_again) Try again")
    # create a new instance b/c the current one is too shit
    find_create_confirm_instance(0, instance_num)


def handler_kickit(event, context):
    num_instances = 1 if TRANSCRIBER_NUM_INSTANCES is None else int(TRANSCRIBER_NUM_INSTANCES)
    for i in range(num_instances):
        print(f" ------- {i} -------")
        print("handler_kickit() TRANSCRIBER_NUM_INSTANCES", TRANSCRIBER_NUM_INSTANCES)
        print("handler_kickit() creating instance # ", i)
        find_create_confirm_instance(0, i)
        time.sleep(60) # wait 1 minute

if __name__ == '__main__':
    find_create_confirm_instance(0, 0)
    