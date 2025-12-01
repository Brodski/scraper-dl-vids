
import time
import urllib.request
import urllib.parse
import json
from configz import *

def get_my_instance_baby(id):
    url = f"https://console.vast.ai/api/v0/instances/{id}/?owner=me&api_key=" + VAST_API_KEY
    with urllib.request.urlopen(url) as response:
        data = response.read()  # Read response bytes
        json_data = json.loads(data)  # Parse JSON
    print(json_data)
    return(json_data["instances"])

def get_my_instances():
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

        