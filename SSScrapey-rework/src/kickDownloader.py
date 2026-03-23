import sys
from typing import Dict, List
from env_file import env_varz
env_varz.init_argz()

import time
import controllers.MicroDownloader.downloaderGo as downloadGo
import controllers.MicroDownloader.downloader as downloadDb
import utils.generic_stuff as utils_generic
from models.Vod import Vod
import threading
import os

def timeout():
    print("Timeout! Exiting.")
    os._exit(1)

if __name__ == "__main__":
    print('starting go download batch...')
    
    ############
    # CLI ARGS #
    ############
    if env_varz.dwn_query_todo == True:    # $ python .\kickDownloader.py --dwn_query_todo --env locl
        vods_list = downloadDb.getTodoFromDatabase()
        utils_generic.convertToFancyMap(vods_list)
        sys.exit(0)
        # ^ auto prints

    ##############
    # GO BABY GO #
    ##############
    start_time = time.time()
    isDebug=False
    timer = threading.Timer(43200, timeout)  # 12 hours = 43200 seconds
    timer.start()

    try:
        downloadGo.goDownloadBatch(isDebug)
    finally:
        timer.cancel()

    elapsed_time = time.time() - start_time

    print('Finished kickDownloader')
    print("-------------------")
    print("Total time: ", str(int(elapsed_time)), "sec")
    print("-------------------")