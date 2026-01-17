from typing import Dict, List
from env_file import env_varz
env_varz.init_argz()

import time
import controllers.MicroDownloader.downloaderGo as downloadGo
import controllers.MicroTranscriber.transcriberGo as transcriberGo
import controllers.MicroPreper.preperGo as preperGo
from models.Vod import Vod


#############################################################################################################################################
#
#
# python .\kickAllBaby.py --env prod
#
#
#############################################################################################################################################
LOOPER                                 = 2
env_varz.DWN_BATCH_SIZE                = "1"
env_varz.TRANSCRIBER_VODS_PER_INSTANCE = 20
env_varz.TRANSCRIBER_NUM_INSTANCES     = "1"
env_varz.TRANSCRIBER_INSTANCE_CNT      = "1_localx"
env_varz.LOCAL_GPU_RUN                 = True
env_varz.DWN_IS_SKIP_DONT_DELETE       = True

# env_varz.PREP_NUM_CHANNELS=60  
# env_varz.PREP_NUM_VOD_PER_CHANNEL=3

def print_time_it(start_time):
    elapsed_time = time.time() - start_time
    secs = int(elapsed_time)
    min =  secs / 60
    hour = min / 60
    print("-------------------")
    print(f"Total time: {int(elapsed_time)} sec = {min:.2f} min = {hour:.2f} hour")
    print("-------------------")


if __name__ == "__main__":
    print('starting go BOTH DL and Transcribe...')

    print('=============================')
    print('======                  =====')
    print('======      PREPER      =====')
    print('======                  =====')
    print('=============================')
    start_time = time.time()
    
    #################
    #               #
    #   BOOOOOOOM   #
    #               #
    #################
    # preperGo.prepare()

    print('Finished preper')
    print_time_it(start_time)

    max_time = time.time()
    for i in range(LOOPER):
        print('=================================')
        print('======                      =====')
        print('======      DOWNLAODER      =====')
        print('======                      =====')
        print('=================================')
        start_time = time.time()

        ### BOOOOOOOM ###
        downloadGo.goDownloadBatch(False)

        print('Finished downloader')
        print_time_it(start_time)



        print('==================================')
        print('======                       =====')
        print('======      TRANSCRIBER      =====')
        print('======                       =====')
        print('==================================')
        start_time = time.time()
        
        ### BOOOOOOOM ###
        transcriberGo.goTranscribeBatch(False)

        print('Finished downloader')
        print_time_it(start_time)

    print(" ------- MEGA TOTAL ------------")
    print(f"LOOPER = {LOOPER}")
    print(f"env_varz.DWN_BATCH_SIZE = {env_varz.DWN_BATCH_SIZE}")
    print(f"env_varz.TRANSCRIBER_VODS_PER_INSTANCE = {env_varz.TRANSCRIBER_VODS_PER_INSTANCE}")


    print_time_it(max_time)