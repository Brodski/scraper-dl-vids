
import time
from typing import List
import urllib.request
import urllib.parse
import json
from Configz import configz
from Instance_V import Instance_V
from Instance_V import Status

def get_all_instances(instance_v_list: List[Instance_V]):
    url = f"https://console.vast.ai/api/v0/instances/?owner=me&api_key=" + configz.VAST_API_KEY
    print("get_my_instance_baby - url")
    print(url)
    vast_data_dictionary: dict = {}
    with urllib.request.urlopen(url) as response:
        data = response.read()
        json_data = json.loads(data)    
        for instance in json_data["instances"]:
            vast_data_dictionary[instance["id"]] = instance # { 12345: {data1}, 67890: {data2}  }

        # x = json_data["instances"]
        # instance_ids = {v.id_contract for v in instance_v_list}
        # data_intersection = [
        #     item for item in json_data["instances"] if item.get("id") in instance_ids
        # ]
    return vast_data_dictionary

def get_my_instance_baby(id):
    url = f"https://console.vast.ai/api/v0/instances/{id}/?owner=me&api_key=" + configz.VAST_API_KEY
    print("get_my_instance_baby - url")
    print(url)
    # https://console.vast.ai/api/v0/instances/29095744/?owner=me&api_key=cc6e359e54b0fb85559289d1e5ffb2551d14e45176ac12ae717e5b229a03b8f2
    # https://console.vast.ai/api/v0/instances/?owner=me&api_key=cc6e359e54b0fb85559289d1e5ffb2551d14e45176ac12ae717e5b229a03b8f2
    with urllib.request.urlopen(url) as response:
        data = response.read()  # Read response bytes
        json_data = json.loads(data)  # Parse JSON
    # print(json_data[:50])
    return(json_data["instances"])

def get_my_instances():
    url = "https://console.vast.ai/api/v0/instances?owner=me&api_key=" + configz.VAST_API_KEY
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
    # print(" (get_my_instances) current running instances (if any): ")
    # printAsTable(rows)
    return(rows)


def printDebug(id_contract):
    rows = get_my_instances()
    for row in rows:
        row_id = str(row['id'])
        print("    (printDebug) row_id", row_id)
        if row_id == id_contract:
            print("WE ARE USING THIS INSTANCE!")
            print("WE ARE USING THIS INSTANCE!")
            print("WE ARE USING THIS INSTANCE!")
            print("WE ARE USING THIS INSTANCE!")
            print()
            print(json.dumps(row, indent=4))
            break


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

        