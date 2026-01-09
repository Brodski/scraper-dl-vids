import sys
from typing import Dict, List
from env_file import env_varz
env_varz.init_argz()

import time
import controllers.MicroDownloader.downloaderGo as downloadGo
import controllers.MicroDownloader.downloader as downloadDb
import utils.generic_stuff as utils_generic
from models.Vod import Vod



if __name__ == "__main__":
    print('starting go download batch...')
    env_varz.MICRO_APP_TYPE = "downloader"
    
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
    downloadGo.goDownloadBatch(isDebug)

    elapsed_time = time.time() - start_time

    print('Finished kickDownloader')
    print("-------------------")
    print("Total time: ", str(int(elapsed_time)), "sec")
    print("-------------------")