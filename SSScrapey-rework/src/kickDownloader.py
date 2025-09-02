import time
import controllers.MicroDownloader.downloaderGo as downloadGo


if __name__ == "__main__":
    print('starting go download batch...')

    start_time = time.time()

    x = downloadGo.goDownloadBatch(isDebug=False)

    print('Finished kickDownloader')

    elapsed_time = time.time() - start_time
    print("-------------------")
    print("Total time: ", elapsed_time)
    print("-------------------")