import os
from env_file import env_varz
env_varz.init_argz()
import time
from typing import Dict, List
import controllers.MicroDownloader.downloaderGo as downloadGo
import controllers.MicroDownloader.downloader as downloadDb
from env_file import env_varz
from controllers.MicroDownloader.downloader import convertVideoToSmallAudio
from controllers.MicroDownloader.downloader import getCompressNeedFromDatabase
import utils.generic_stuff as utils_generic
from models.Vod import Vod



import boto3 # boto3 comes for free in all lambda :o

if __name__ == "__main__":
    print('starting go compress batch...')

    s3 = boto3.client("s3")

    ##############
    # GO BABY GO #
    ##############
    start_time = time.time()
    isDebug=False

    vods_list       = getCompressNeedFromDatabase(0, isDebug=isDebug) # "vod" is highest priority 'todo' vod
    magical_ordered_map: Dict[int, List[Vod]]  = utils_generic.convertToFancyMap(vods_list)
    gen             = utils_generic.getFromFancyMap(magical_ordered_map)      # <--- smart
    vod: Vod        = next(gen, None)

    
    bucket    = "my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket"
    key = f"channels/vod-audio/{vod.channels_name_id}/{vod.id}/{vod.title}.mp4"


    output_local_dir = os.path.normpath("assets/audio") # saving at ./assets/audio/{filename}
    download_path = f"./assets/output/{vod.channels_name_id}-v{vod.id}.opus"
    s3.download_file(bucket, key, download_path)
    convertVideoToSmallAudio(download_path)
    downloadGo.goDownloadBatch(isDebug)

    elapsed_time = time.time() - start_time

    print('Finished kickCompess')
    print("-------------------")
    print("Total time: ", str(int(elapsed_time)))
    print("-------------------")