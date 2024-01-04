import controllers.MicroDownloader.downloader as downloader
from models.Vod import Vod
from typing import List
import env_file as env_varz

def goDownloadBatch(isDebug=False):
    download_batch_size = int(env_varz.DWN_BATCH_SIZE)
    for i in range(0, download_batch_size):
        print("===================================")
        print(f"    DOWNLOAD BATCH - COUNT: {i}  ")
        print("===================================")
        x = download(isDebug)
    return x

def download(isDebug=False):
    vod = downloader.getTodoFromDatabase(isDebug=isDebug) # limit = 5
    if vod == None:
        print("There are zero transcript_status='todo' from the query :O")
        return "nothing to do"
    # Download vod from twitch
    isSuccess = downloader.lockVodDb(vod, isDebug)
    if not isSuccess:
        print("No VODS todo!")
        return "No VODS todo!"
    downloaded_metadata = downloader.downloadTwtvVid2(vod, True)
    if downloaded_metadata == "403":
        downloader.updateErrorVod(vod,"unauthorized")
        return "nope gg sub only"
    if downloaded_metadata == "404":
        downloader.updateErrorVod(vod, "deleted")
        return "nope gg sub only"
    if downloaded_metadata == None:
        downloader.updateErrorVod(vod, "unknown")
        return "nope gg. Some other error"

    # Post process vod
    downloaded_metadata = downloader.removeNonSerializable(downloaded_metadata)
    downloaded_metadata, outfile = downloader.convertVideoToSmallAudio(downloaded_metadata)

    # Upload DB
    s3fileKey = downloader.uploadAudioToS3_v2(downloaded_metadata, outfile, vod)
    if (s3fileKey):
        downloader.updateVods_Round2Db(downloaded_metadata, vod.id, s3fileKey)
    downloader.cleanUpDownloads(downloaded_metadata)

    print("Finished step 2 Downloader-Service")
    return downloaded_metadata