import controllers.MicroDownloader.downloader as downloader
from models.Vod import Vod
from typing import List
import env_file as env_varz
from controllers.MicroDownloader.errorEnum import Errorz

def printIntro():
    print("db      =" , env_varz.DATABASE)
    print("host    =" , env_varz.DATABASE_HOST)
    print("user    =" , env_varz.DATABASE_USERNAME)
    print("Will download this many: ")
    print("DWN_BATCH_SIZE:", env_varz.DWN_BATCH_SIZE)
    print("There is only 1 ecs instance for Downloader. Nothing crazy")
    # Note: DWN_QUERY_PER_RECENT doesnt have much effect. Looks at X recent vods from the database (todo, completed, audio2text_need, ect) then gets the "todo" one
    #       It is so that we dont over prioritize all the vods from the 'top streamers'
def goDownloadBatch(isDebug=False):
    printIntro()
    download_batch_size = int(env_varz.DWN_BATCH_SIZE)
    i = 0
    gaurdrail = 25
    while i < download_batch_size and i < gaurdrail:
        gaurdrail -= 1
        print("===========================================")
        print(f"    DOWNLOAD BATCH - {i+1} of {download_batch_size}  ")
        print("===========================================")
        dl_meta = download(i, isDebug)
        if dl_meta == Errorz.TOO_BIG or dl_meta == Errorz.DELETED_404 or dl_meta == Errorz.UNAUTHORIZED_403:
            print("We skipped a download, trying next entry. Error:", dl_meta)
            continue
        print(f"Finished download # {i} of {download_batch_size}")
        i += 1
    return dl_meta

def download(i, isDebug=False):
    vod = downloader.getTodoFromDatabase(i, isDebug=isDebug) # limit = 5
    if vod == None:
        print("There are zero transcript_status='todo' from the query :O")
        return "nothing to do"
    # Download vod from twitch
    vod.printDebug()
    isSuccess = downloader.lockVodDb(vod, isDebug)
    if not isSuccess:
        print("No VODS todo!")
        return "No VODS todo!"

    print(f"    (download) Going to download: {vod.channels_name_id} - {vod.id} - {vod.title}")
    print(f"    (download) highest priority vod. name: {vod.channels_name_id}")
    print(f"    (download) highest priority vod. id: {vod.id}")
    print(f"    (download) highest priority vod. title: {vod.title}")
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
        json_s3_img_keys = downloader.updateImgs_Db(downloaded_metadata, vod)
        downloader.updateVods_Db(downloaded_metadata, vod.id, s3fileKey, json_s3_img_keys)
    downloader.cleanUpDownloads(downloaded_metadata)

    return downloaded_metadata