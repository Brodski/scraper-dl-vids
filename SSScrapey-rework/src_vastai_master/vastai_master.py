import argparse
import time
import traceback
import urllib.request
import urllib.parse
import json
import os
from urllib.parse import quote_plus  # Python 3+
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    print("We are in lambda") # ?????? Why did i write this

#########################################################################
#                                                                       #
# Note: find_create_confirm_instance() is the "main()" Defined in lambda_vastai.tf    #
# Vars: vars_prod.tf locally on -> terraform -> lambda -> python        #  
#                                                                       #
#########################################################################

print("os.environ.get('DOCKER')", os.environ.get('DOCKER'))
print("os.environ.get('DATABASE_HOST')", os.environ.get('DATABASE_HOST'))
print("DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')", os.environ.get('DATABASE_USERNAME'))


VAST_API_KEY = os.environ.get('VAST_API_KEY')
TRANSCRIBER_NUM_INSTANCES = os.environ.get('TRANSCRIBER_NUM_INSTANCES')
AWS_SECRET_ACCESS_KEY = os.environ.get('MY_AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('MY_AWS_ACCESS_KEY_ID')
ENV = os.environ.get('ENV')
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_PORT = os.environ.get('DATABASE_PORT')
DATABASE = os.environ.get('DATABASE')
DOCKER = os.environ.get('DOCKER') or "cbrodski/transcriber:official_v2"

# ############################################
#
#                  CONFIGS 
# Instance most be greater/less than these:
#
# ############################################
dph = "0.40" # 0.30 dollars / hour
# dph = "0.12"
cuda_vers = "12"
cpu_ram = "16000.0"
disk_space = "32"
disk = 32.0 # Gb
image = DOCKER 
storage_cost = "0.3"
blacklist_gpus = ["GTX 1070", "RTX 2080 Ti", "GTX 1080 Ti", "RTX 2070S" ]
blacklist_ids = []
inet_down_cost = "0.05"
inet_up_cost = "0.05"
gpu_ram = "23000"

# copied from vast ai github https://github.com/vast-ai/vast-python/blob/d379d81c420f0f450b5759e3517d68ad89e1c39d/vast.py#L195
def requestOffersHttp(query_args):
    query_args["api_key"] = VAST_API_KEY
    query_json = "&".join("{x}={y}".format(x=x, y=quote_plus(y if isinstance(y, str) else json.dumps(y))) for x, y in query_args.items())
    # https://console.vast.ai/api/v0/bundles?q=%7B%22verified%22%3A+%7B%22eq%22%3A+true%7D%2C+%22external%22%3A+%7B%22eq%22%3A+false%7D%2C+%22rentable%22%3A+%7B%22eq%22%3A+true%7D%2C+%22dph%22%3A+%7B%22lt%22%3A+%220.12%22%7D%2C+%22dph_total%22%3A+%7B%22lt%22%3A+%220.12%22%7D%2C+%22cuda_vers%22%3A+%7B%22gte%22%3A+%2212%22%7D%2C+%22cuda_max_good%22%3A+%7B%22gte%22%3A+%2212%22%7D%2C+%22cpu_ram%22%3A+%7B%22gt%22%3A+16000.0%7D%2C+%22order%22%3A+%5B%5B%22cpu_ram%22%2C+%22asc%22%5D%5D%2C+%22type%22%3A+%22on-demand%22%7D&api_key=999999999999999999
    theRequest = "https://console.vast.ai/api/v0/bundles?" + query_json 
    url = theRequest
    print("theRequest: " + theRequest)
    response = urllib.request.urlopen(url)
    if response.status != 200:
        print('exiting, status not 200')
        exit()
    data = response.read()
    json_data = json.loads(data)
    return json_data.get("offers")

def create_instance(instance_id):
    url = "https://console.vast.ai/api/v0/asks/" + str(instance_id) + "/?api_key=" + VAST_API_KEY
    print("    (create_instance)  url: ", url)
    print("    (create_instance)  DOCKER IAMGE: ", image)
    print("    (create_instance)  DOCKER IAMGE: ", image)
    print("    (create_instance)  DOCKER IAMGE: ", image)
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
                'VAST_API_KEY': VAST_API_KEY
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
    if os.environ.get('ENV') == None or os.environ.get('ENV') == "local":
        print("ending early b/c local\n" *9)
        exit(0)
    request = urllib.request.Request(url, data=data_json, method='PUT')

    id = None
    with urllib.request.urlopen(request) as response:
        response_data = response.read()
        res_json = json.loads(response_data.decode('utf-8'))
        print(    "(create_instance) res_json: ", res_json)
        id = res_json.get("new_contract")
    print(    "(create_instance) Created :)")
    return id

# Again, copy pasted
def show_my_instances():
    url = "https://console.vast.ai/api/v0/instances?owner=me&api_key=" + VAST_API_KEY
    print(f"  (show_my_instances) getting info at: {url}")
    response = urllib.request.urlopen(url)
    if response.status != 200:
        print('sadge')
        exit()
    data = response.read()
    json_data = json.loads(data)
    # print(f"  (show_my_instances) json_data: {json_data}")
    rows = json_data.get("instances")
    for row in rows:
        row['duration'] = time.time() - row['start_date'] 
        print("id: " + str(row['id']) + ", time running: " + str(row['duration']))
    print(" (show_my_instances) current running instances (if any): ")
    printAsTable(rows)
    return(rows)

def destroy_instance(id):
    print("Destryoing instance: " + str(id))
    url = "https://console.vast.ai/api/v0/instances/" + id + "/?api_key=" + VAST_API_KEY
    data_dict = {}
    data_json = json.dumps(data_dict).encode('utf-8')

    request = urllib.request.Request(url, data=data_json, method='DELETE')
    with urllib.request.urlopen(request) as response:
        response_data = response.read()
        print(response_data.decode('utf-8'))

        status_code = response.getcode()
        print("Status Code:", status_code)
    print("DONE :)")



def printAsTable(goodOffers):
    if (len(goodOffers) == 0):
        print("    (printAsTable) wtf goodOffers == 0, returning")
        return
    # print(goodOffers[0])
    headers = ["id", "gpu_name", "dph_total", "dlperf", "inet_down_cost", "inet_up_cost", "storage_cost", "dlperf_per_dphtotal", "gpu_ram", "cpu_ram", "cpu_cores", "disk_space", "inet_up", "inet_down", "score", "cuda_max_good", "machine_id", "geolocation", "reliability2" ]
    def printColAux(column):
        if column is None:
            column = "None!"
        p = f"{column:<11}"
        # p = f"{column:<8}"
        print(str(p)[:11] + "  ", end="")
    print()
    for column in headers:
        printColAux(column)
    print()
    for offer in goodOffers:
        for head in headers:
            printColAux(offer.get(head, "failed?"))
        print()

        
        
def find_create_confirm_instance(event, context, rerun_count):
    if (rerun_count >= 2):
        print("  (find_create_confirm_instance) We have reran too many time,  ENDING!\n" * 3)
        return
    print("  (find_create_confirm_instance) BEGIN!")
    print("  (find_create_confirm_instance) aws event:")
    print(event)

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
    dataz = json.loads(everything_request)
    x = json.dumps(dataz, indent=2)
    offers = requestOffersHttp(json.loads(everything_request))
    offerz = json.dumps(offers, indent=2)
    # print("  (find_create_confirm_instance) offers[0]")
    # print(json.dumps(offers[0], indent=2))
    print("  (find_create_confirm_instance) == GO BABY GO ==")
    # print("== All offers below ==")
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
        print("ADDING " + id)
        goodOffers.append(offer)
    
    goodOffers = sorted(goodOffers, key=lambda x: x['dph_total'])
    print("  (find_create_confirm_instance)  offers COUNT: " + str(len(offers)))
    print("  (find_create_confirm_instance)  Number of goodOffers: ", len(goodOffers))
    if len(goodOffers) == 0:
        print("THERE ARE NO GOOD OFFERS!\n" * 9)
        print("Gonna try again in 5 min")
        time.sleep(150)
        print('2.5 min passed ...')
        time.sleep(150)
        print('5 min passed ...')
        find_create_confirm_instance(event, None, rerun_count + 1)
    print("  (find_create_confirm_instance)  Good offers: ")
    printAsTable(goodOffers)

    instance_first = goodOffers[0]
    print("  (find_create_confirm_instance) instance_first: ", instance_first.get("id"))
    print(f'  (find_create_confirm_instance) "IS_VASTAI_CREATE_INSTANCE": {os.environ.get("IS_VASTAI_CREATE_INSTANCE")}')
    # if create_auto or os.environ.get("IS_VASTAI_CREATE_INSTANCE") == "true": # env set in lambda_vastai.tf
    # exit(0)
    if True:
        try:
            id_create = instance_first.get("id")
            id_contract = create_instance(id_create)
            status = pollCompletion(id_contract, time.time(), 0)
            if status == "success":
                # WE PRINT A LOT OF INFO
                print("Status == 'success' Ya! :D")
                printDebug(id_contract)
            else:
                status = "None" if status is None else status
                print("  (find_create_confirm_instance) POLL FAILED. STATUS=" + status)
                print("  (find_create_confirm_instance) POLL FAILED. STATUS=" + status)
                print("  (find_create_confirm_instance) POLL FAILED. STATUS=" + status)
                print("  (find_create_confirm_instance) POLL FAILED. id_create=", id_create)
                print("  (find_create_confirm_instance) POLL FAILED. id_contract=", id_contract)
                destroy_instance(id_contract)
        except Exception as e:
            traceback.print_exc()
            print(f"   (find_create_confirm_instance) Error creating instacne {e}")
            print(f"   (find_create_confirm_instance) Might try again..")
            find_create_confirm_instance(event, None, rerun_count + 1)
            
    return {
        'statusCode': 200,
        'body': json.dumps('Completed vastai init!! ')
    }
def printDebug(id_contract):
    rows = show_my_instances()
    for row in rows:
        row_id = str(row['id'])
        print("    (printDebug) row_id", row_id)
        print("    (printDebug) id_contract", id_contract)
        if row_id == id_contract:
            print("WE ARE USING THIS INSTANCE!")
            print("WE ARE USING THIS INSTANCE!")
            print("WE ARE USING THIS INSTANCE!")
            print("WE ARE USING THIS INSTANCE!")
            print()
            print(json.dumps(row, indent=4))
            break

def pollCompletion(id_contract, start_time, counter_try_again):
    # id_create = id_contract
    print(f'----- {counter_try_again}: polling {str(id_contract)} for completion -----')
    if counter_try_again > 11: # 11 min
        print(f"    (pollCompletion) counter_try_again > 11. Ending. counter_try_again={counter_try_again}")
        return
    status_msg = None
    actual_status = None
    exec_time_minutes = (time.time() - start_time) / 60
    id_contract = str(id_contract)
    rows = show_my_instances()
    print("    (pollCompletion) exec_time_minutes: ", exec_time_minutes)
    for row in rows:
        row_id = str(row['id'])
        if row_id == id_contract:
            print("    (pollCompletion) status_msg: ", row.get("status_msg"))
            print("    (pollCompletion) actual_status: ", row.get("actual_status"))
            status_msg = row["status_msg"]
            actual_status = row["actual_status"]
            break
    
    if status_msg and status_msg.lower().startswith("unexpected fault address"):
        print("    (pollCompletion) nope not ready, 'unexpected fault address' end it")
        try_again(str(row['id']))
        return
    if status_msg and "unable to find image" in status_msg.lower():
        print("    (pollCompletion) nope not ready, end it")
        try_again(str(row['id']))
        return
    if actual_status and actual_status == "loading" and exec_time_minutes > 7: # 7 minutes. Image is stuck loading
        print("    (pollCompletion) nope not ready and exec_time_minutes > 7 min, end it. exec_time_minutes:", exec_time_minutes)
        try_again(str(row['id']))
        return
    if actual_status and actual_status == "running":
        print("    (pollCompletion) Running, we're done :)")
        return "success"
    print('    (pollCompletion) sleeping for 60 sec')
    time.sleep(60) 
    return pollCompletion(id_contract, start_time, counter_try_again+1)

def try_again(id):
    print("   ! (try_again) end it")
    destroy_instance(id)
    blacklist_ids.append(id)
    print("   ! (try_again) Try again")
    print("   ! (try_again) Try again")
    print("   ! (try_again) Try again")
    # create a new instance b/c the current one is too shit
    find_create_confirm_instance(None, None, 0)


def handler_kickit(event, context):
    num_instances = 1 if TRANSCRIBER_NUM_INSTANCES is None else int(TRANSCRIBER_NUM_INSTANCES)
    print("TRANSCRIBER_NUM_INSTANCES", TRANSCRIBER_NUM_INSTANCES)
    for i in range(num_instances):
        print("handler_kickit() beign loop:", i)
        find_create_confirm_instance(event, context, 0)
        time.sleep(60) # wait 1 minute

if __name__ == '__main__':
    find_create_confirm_instance(None, None, 0)
    
    
    

    # "id": 6585613,
    # "gpu_name": "A100 SXM4",
    # "dlperf": 70.164811,
    # "dph_total": 7.16,
    # "cuda_max_good": 12.0,
    # "machine_id": 11611,
    # "inet_down_cost": 0.0,
    # "inet_up_cost": 0.0,
    # "storage_cost": 0.149,
    # "dlperf_per_dphtotal": 9.799554608938548,
    # "reliability2": 1233,
    # "cpu_ram": 403103,
    # "cpu_cores": 32,
    # "disk_space": 299.7,
    # "inet_up": 953.6,
    # "inet_down": 950.4,
    # "score": 8.285414375740809,
    # "geolocation": "Czechia, CZ",


    # specific_request = (
    #      f'{{'
    #         f'"q":{{ '
    #             f'"verified": {{"eq": true}},'
    #             f'"external": {{"eq": false}},'
    #             f'"rentable": {{"eq": true}},'

    #             f'"dph": {{"lt": "{dph}"}},'
    #             f'"dph_total": {{"lt": "{dph}"}},'
    #             f'"cuda_vers": {{"gte": "{cuda_vers}"}},'
    #             f'"cuda_max_good": {{"gte": "{cuda_vers}"}},'
    #             f'"cpu_ram": {{"gt": {cpu_ram}}},'
    #             # "dph": {"lt": "0.12"},
    #             # "dph_total": {"lt": "0.12"},
    #             # "cuda_vers": {"gte": "12"},
    #             # "cuda_max_good": {"gte": "12"},
    #             # "cpu_ram": {"gt": 16000.0},
    #             f'"order":[[   "cpu_ram",   "asc"] ],'

    #             f'"type":"on-demand"'
    #             f'}}'
    #         f'}}'
    # )
