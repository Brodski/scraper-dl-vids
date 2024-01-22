import argparse
import time
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
# Note: handler_kickit() is the "main()" Defined in lambda_vastai.tf    #
# Vars: vars_prod.tf locally on -> terraform -> lambda -> python        #  
#                                                                       #
#########################################################################

print("os.environ.get('DOCKER')", os.environ.get('DOCKER'))
print("os.environ.get('DATABASE_HOST')", os.environ.get('DATABASE_HOST'))
print("DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')", os.environ.get('DATABASE_USERNAME'))


VAST_API_KEY = os.environ.get('VAST_API_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('MY_AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('MY_AWS_ACCESS_KEY_ID')
ENV = os.environ.get('ENV')
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE = os.environ.get('DATABASE')
DOCKER = os.environ.get('DOCKER') or "cbrodski/transcriber:official_v2"

# 'configs'
dph = "0.12"
cuda_vers = "12"
cpu_ram = "16000.0"
disk_space = "32"
disk = 32.0 # Gb
image = DOCKER 
storage_cost = "0.3"
blacklist_gpus = ["GTX 1070"]
blacklist_ids = []

counter_try_again = 0
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
    print("create_instance url: ")
    print(url)
    data_dict =  {  
        "client_id": "me",
        "image": image, 
        "env": {'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY, 
                'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID,
                'ENV': ENV,
                'DATABASE_HOST': DATABASE_HOST,
                'DATABASE_USERNAME': DATABASE_USERNAME,
                'DATABASE_PASSWORD': DATABASE_PASSWORD,
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
        print("ending early b/c local")
        return
    request = urllib.request.Request(url, data=data_json, method='PUT')

    with urllib.request.urlopen(request) as response:
        response_data = response.read()
        print(response_data.decode('utf-8'))
    print("Created :)")

# Again, copy pasted
def show_instances():
    url = "https://console.vast.ai/api/v0/instances?owner=me&api_key=" + VAST_API_KEY
    response = urllib.request.urlopen(url)
    if response.status != 200:
        print('sadge')
        exit()
    data = response.read()
    json_data = json.loads(data)
    rows = json_data.get("instances")
    for row in rows:
        row['duration'] = time.time() - row['start_date'] 
        print("id: " + str(row['id']) + ", time running: " + str(row['duration']))
    print("- My current running instances (if any) -")
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
    headers = ["id", "gpu_name", "dph_total", "dlperf", "inet_down_cost", "inet_up_cost", "storage_cost", "dlperf_per_dphtotal", "reliability2", "cpu_ram", "cpu_cores", "disk_space", "inet_up", "inet_down", "score", "cuda_max_good", "machine_id", "geolocation", "reliability2" ]
    def printColAux(column):
        p = f"{column:<8}"
        print(str(p)[:8] + "  ", end="")
    print()
    for column in headers:
        printColAux(column)
    print()
    for offer in goodOffers:
        for head in headers:
            printColAux(offer.get(head))
        print()

        
def handler_kickit(event, context):
    print("handler_kickit() beign")
    print("event:")
    print(event)
    create_auto = False

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
    print("offerz[0]")
    print(offerz[0])
    print("== GO BABY GO ==")
    # print("== All offers below ==")
    # printAsTable(offers)
    good_offers_counter = 0
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
        if offer.get("storage_cost") > float(storage_cost):
            print(id + " skipping storage_cost: " + str(offer.get("storage_cost")))
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
        good_offers_counter = good_offers_counter + 1
    

    print("offers COUNT: " + str(len(offers)))
    print("good_offers_counter: " + str(good_offers_counter))
    goodOffers = sorted(goodOffers, key=lambda x: x['dph_total'])
    print("+++++ Good offers: +++++")
    printAsTable(goodOffers)
    instance_first = goodOffers[0]
    print("instance_first: ", instance_first.get("id"))
    print(f'os.environ.get("IS_VASTAI_CREATE_INSTANCE"): {os.environ.get("IS_VASTAI_CREATE_INSTANCE")}')
        
    if create_auto or os.environ.get("IS_VASTAI_CREATE_INSTANCE") == "true": # env set in lambda_vastai.tf
        id_create = instance_first.get("id")
        create_instance(id_create)
        pollCompletion(id_create, time.time(), counter_try_again)
    return {
        'statusCode': 200,
        'body': json.dumps('Completed vastai init!! ')
    }

def pollCompletion(id_create, start_time, counter_try_again):
    print(f'---- start time epoch: {str(start_time)} -----')
    print(f'polling {str(id_create)} for completion')
    if counter_try_again > 14: # 14 min
        print(f"counter_try_again > 14. Ending. counter_try_again={counter_try_again}")
        return
    time.sleep(60) 
    status_msg = None
    actual_status = None
    execution_time = (time.time() - start_time) * 60
    id_create = str(id_create)
    rows = show_instances()
    print("execution_time: ", execution_time)
    for row in rows:
        row_id = str(row['id'])
        if row_id == id_create:
            status_msg = row["status_msg"]
            actual_status = row["actual_status"]
            print("status_msg: ", status_msg)
            print("actual_status: ", actual_status)
            break
    
    print("(after loop) status_msg: ", status_msg)
    print("(after loop) actual_status: ", actual_status)
    if status_msg and "unable to find image" in status_msg.lower():
        print("nope not ready, end it")
        try_again(str(row['id']))
        return
    if actual_status and actual_status == "loading" and execution_time > 11: # 11 minutes. Image is stuck loading
        print("nope not ready and execution_time > 11min, end it")
        try_again(str(row['id']))
        return
    if actual_status and actual_status == "running":
        print("Running, we're done :)")
        return
    return pollCompletion(id_create, start_time, counter_try_again+1)

def try_again(id):
    print("end it")
    destroy_instance(id)
    blacklist_ids.append(id)
    handler_kickit(None, None)

if __name__ == '__main__':
    handler_kickit(None, None)
    
    
    

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
