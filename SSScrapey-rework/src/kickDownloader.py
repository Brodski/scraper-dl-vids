import time
import controllers.MicroDownloader.downloaderGo as downloadGo
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--quick-dl", action="store_true", help="downloads quick")

args = parser.parse_args()


if __name__ == "__main__":
    print('starting go download batch...')

    start_time = time.time()
    isDebug=False

    downloadGo.goDownloadBatch(isDebug, args)

    print('Finished kickDownloader')

    elapsed_time = time.time() - start_time
    print("-------------------")
    print("Total time: ", elapsed_time)
    print("-------------------")