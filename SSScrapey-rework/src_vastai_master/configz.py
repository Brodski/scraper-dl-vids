# ############################################
#
#                  CONFIGS 
# Instance most be greater/less than these:
#
# ############################################
import os
from configz import *

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    print("We are in lambda") # ?????? Why did i write this


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