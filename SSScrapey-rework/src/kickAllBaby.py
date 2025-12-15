from typing import Dict, List
from env_file import env_varz
env_varz.init_argz()

import time
import controllers.MicroDownloader.downloaderGo as downloadGo
import controllers.MicroTranscriber.transcriberGo as transcriberGo
import controllers.MicroPreper.preperGo as preperGo
from models.Vod import Vod


#
#
#
# python .\kickAllBaby.py --env local --transcriber_vods_per_instance 2 --transcriber_num_instances 1 --transcriber_instance_cnt 1
#
#
#


def print_time_it(start_time):
    elapsed_time = time.time() - start_time
    print("-------------------")
    print("Total time: ", str(int(elapsed_time)))
    print("-------------------")

if __name__ == "__main__":
    print('starting go BOTH DL and Transcribe...')

    print('=============================')
    print('======                  =====')
    print('======      PREPER      =====')
    print('======                  =====')
    print('=============================')
    start_time = time.time()
    
    ### BOOOOOOOM ###
    # preperGo.prepare()

    print('Finished preper')
    print_time_it(start_time)

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