import controllers.MicroDownloader.downloader as downloader
from models.Vod import Vod
from typing import List
import env_file as env_varz

def goDownloadBatch(isDebug=False):
    download_batch_size = int(env_varz.DWN_BATCH_SIZE)
    print(f"DOWNLOAD BATCH SIZE: {download_batch_size}")
    for i in range(0, download_batch_size):
        print("===========================================")
        print(f"    DOWNLOAD BATCH - {i+1} of {download_batch_size}  ")
        print("===========================================")
        x = download(isDebug)
        print(f"Finished Index {i}")
        print(f"download_batch_size: {i}")
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
    # downloaded_metadata = downloader.downloadTwtvVid2(vod, True)
    downloaded_metadata = downloader.downloadTwtvVidFAST(vod)
    if downloaded_metadata == "403":
        downloader.updateErrorVod(vod,"unauthorized")
        msg = "nope gg. 403 sub only"
        print(msg)
        return msg
    if downloaded_metadata == "404":
        downloader.updateErrorVod(vod, "deleted")
        msg = "nope gg. 404 delete"
        print(msg)
        return msg
    if downloaded_metadata == "vod too big":
        downloader.updateErrorVod(vod, "too_big")
        msg = "nope gg. too big"
        print(msg)
        return msg
    if downloaded_metadata == None:
        downloader.updateErrorVod(vod, "unknown")
        msg = "nope gg. Some other error"
        print(msg)
        return msg

    # Post process vod
    downloaded_metadata = downloader.removeNonSerializable(downloaded_metadata)
    downloaded_metadata, outfile = downloader.convertVideoToSmallAudio(downloaded_metadata)
    # Upload DB
    s3fileKey = downloader.uploadAudioToS3_v2(downloaded_metadata, outfile, vod)
    if (s3fileKey):
        downloader.updateVods_Round2Db(downloaded_metadata, vod.id, s3fileKey)
    downloader.cleanUpDownloads(downloaded_metadata)

    return downloaded_metadata