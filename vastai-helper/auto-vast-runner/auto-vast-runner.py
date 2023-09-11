# from urllib import request
import urllib.request
import urllib.parse
import json
import os
# import argparse
from urllib.parse import quote_plus  # Python 3+
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    print("We are in lambda")
VAST_API_KEY = os.environ.get('VAST_API_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('MY_AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('MY_AWS_ACCESS_KEY_ID')

# 'configs'
dph = "0.12"
cuda_vers = "12"
cpu_ram = "16000.0"
disk_space = "32"
disk = 32.0 # Gb
image = "cbrodski/audio2text:latest"
storage_cost = "0.3"
blacklist_gpus = ["GTX 1070"]

# copied from vast ai github https://github.com/vast-ai/vast-python/blob/d379d81c420f0f450b5759e3517d68ad89e1c39d/vast.py#L195
def requestOffersHttp(query_args):
    query_args["api_key"] = VAST_API_KEY
    query_json = "&".join("{x}={y}".format(x=x, y=quote_plus(y if isinstance(y, str) else json.dumps(y))) for x, y in query_args.items())
    print("query_json")
    print(query_json)
    # https://console.vast.ai/api/v0/bundles?q=%7B%22verified%22%3A+%7B%22eq%22%3A+true%7D%2C+%22external%22%3A+%7B%22eq%22%3A+false%7D%2C+%22rentable%22%3A+%7B%22eq%22%3A+true%7D%2C+%22dph%22%3A+%7B%22lt%22%3A+%220.12%22%7D%2C+%22dph_total%22%3A+%7B%22lt%22%3A+%220.12%22%7D%2C+%22cuda_vers%22%3A+%7B%22gte%22%3A+%2212%22%7D%2C+%22cuda_max_good%22%3A+%7B%22gte%22%3A+%2212%22%7D%2C+%22cpu_ram%22%3A+%7B%22gt%22%3A+16000.0%7D%2C+%22order%22%3A+%5B%5B%22cpu_ram%22%2C+%22asc%22%5D%5D%2C+%22type%22%3A+%22on-demand%22%7D&api_key=999999999999999999
    theRequest = "https://console.vast.ai/api/v0/bundles?" + query_json 
    url = theRequest
    print("theRequest")
    print(theRequest)
    response = urllib.request.urlopen(url)
    if response.status != 200:
        print('sadge')
        exit()
    data = response.read()
    json_data = json.loads(data)
    return json_data.get("offers")

def create_instance(instance_id):
    url = "https://console.vast.ai/api/v0/asks/" + str(instance_id) + "/?api_key=" + VAST_API_KEY
    print("url: ")
    print(url)
    data_dict =  {  
        "client_id": "me",
        "image": image, 
        "env": {'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY, 'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID}, 
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
    request = urllib.request.Request(url, data=data_json, method='PUT')

    with urllib.request.urlopen(request) as response:
        response_data = response.read()
        print(response_data.decode('utf-8'))
    print("DONE :)")


def printAsTable(goodOffers):
    # Print shit
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
    create_auto = False
    # parser = argparse.ArgumentParser(description="Arg parser :D")
    # parser.add_argument("--create-auto",  action="store_true", help="Set if you want to create")
    # args = parser.parse_args()

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
    print("======================")
    print("======================")
    print("======================")
    print("======================")
    print("======================")
    offers = requestOffersHttp(json.loads(everything_request))
    x = json.dumps(offers, indent=2)
    print(x)
    print("== GO BABY GO ==")
    counter = 0
    goodOffers = []
    for offer in offers:
        if offer.get("cuda_max_good") < int(cuda_vers):
            # print("skipping cuda_max_good: " + str(offer.get("cuda_max_good")))
            continue
        if offer.get("dph_total") > float(dph):
            # print("skipping dph: " + str(offer.get("dph")))
            continue
        if offer.get("cpu_ram") < float(cpu_ram):
            # print("skipping cpu_ram: " + str(offer.get("cpu_ram")))
            continue
        if offer.get("disk_space") < float(disk_space):
            # print("skipping disk_space: " + str(offer.get("disk_space")))
            continue
        if offer.get("storage_cost") > float(storage_cost):
            print("skipping storage_cost: " + str(offer.get("storage_cost")))
            continue
        if offer.get("gpu_name") in blacklist_gpus:
            print("skipping blacklist_gpus: " + str(offer.get("gpu_name")))
            continue
        print("======================")
        goodOffers.append(offer)
        counter = counter + 1
    

    print("offers COUNT: " + str(len(offers)))
    print("counter: " + str(counter))
    goodOffers = sorted(goodOffers, key=lambda x: x['dph_total'])
    instance_first = goodOffers[0]
    print("instance_first")
    print(instance_first.get("id"))
    print(instance_first.get("id"))
    print(instance_first.get("id"))

    printAsTable(goodOffers)
        
    if create_auto or os.environ.get("IS_CREATE_INSTANCE") == "true": # env set in vast_lambda.tf
        # print(f"create_auto: {args.create_auto}")
        print(f'os.environ.get("IS_CREATE_INSTANCE"): {os.environ.get("IS_CREATE_INSTANCE")}')
        create_instance(instance_first.get("id"))
    # exit()

if __name__ == '__main__':
    test_event = {}  # Populate with a sample event if needed
    handler_kickit(test_event, None)
    
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



