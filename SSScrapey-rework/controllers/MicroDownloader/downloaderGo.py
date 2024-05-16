import controllers.MicroDownloader.downloader as downloader
from models.Vod import Vod
from typing import List
import env_file as env_varz
from controllers.MicroDownloader.errorEnum import Errorz

def goDownloadBatch(isDebug=False):
    print("db      =" , env_varz.DATABASE)
    print("host    =" , env_varz.DATABASE_HOST)
    print("user    =" , env_varz.DATABASE_USERNAME)
    
    download_batch_size = int(env_varz.DWN_BATCH_SIZE)
    print(f"DOWNLOAD BATCH SIZE: {download_batch_size}")
    # for i in range(0, download_batch_size):
    i = 0
    gaurdrail = 25
    while i < download_batch_size and i < gaurdrail:
        gaurdrail -= 1
        print("===========================================")
        print(f"    DOWNLOAD BATCH - {i+1} of {download_batch_size}  ")
        print("===========================================")
        x = download(isDebug)
        if x == Errorz.TOO_BIG or x == Errorz.DELETED_404 or x == Errorz.UNAUTHORIZED_403:
            print("We skipped a download, trying next entry. Error:", x)
            continue
        print(f"Finished Index {i}")
        print(f"download_batch_size: {i}")
        i += 1
    return x

def download(isDebug=False):
    vod = downloader.getTodoFromDatabase(isDebug=isDebug) # limit = 5
    if vod == None:
        print("There are zero transcript_status='todo' from the query :O")
        return "nothing to do"
    # Download vod from twitch
    vod.printDebug()
    isSuccess = downloader.lockVodDb(vod, isDebug)
    if not isSuccess:
        print("No VODS todo!")
        return "No VODS todo!"
    
    downloaded_metadata = downloader.downloadTwtvVidFAST(vod, isDebug)

    if downloaded_metadata == Errorz.UNAUTHORIZED_403:
        downloader.updateErrorVod(vod,"unauthorized")
        print("nope gg. 403 sub only")
        return Errorz.UNAUTHORIZED_403
    if downloaded_metadata == Errorz.DELETED_404:
        downloader.updateErrorVod(vod, "deleted")
        print("nope gg. 404 delete")
        return Errorz.DELETED_404
    if downloaded_metadata == Errorz.TOO_BIG:
        downloader.updateErrorVod(vod, "too_big")
        print("nope gg. too big")
        return Errorz.TOO_BIG
    if downloaded_metadata == None or downloaded_metadata == Errorz.UNKNOWN:
        downloader.updateErrorVod(vod, "unknown")
        print("nope gg. Some other error")
        return Errorz.UNKNOWN

    # Post process vod
    downloaded_metadata = downloader.removeNonSerializable(downloaded_metadata)
    downloaded_metadata, outfile = downloader.convertVideoToSmallAudio(downloaded_metadata)
    # Upload DB
    s3fileKey = downloader.uploadAudioToS3_v2(downloaded_metadata, outfile, vod)
    if (s3fileKey):
        downloader.updateVods_Round2Db(downloaded_metadata, vod.id, s3fileKey)
    downloader.cleanUpDownloads(downloaded_metadata)

    return downloaded_metadata