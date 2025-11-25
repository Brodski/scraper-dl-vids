import time
import controllers.MicroDownloader.downloaderGo as downloadGo
import controllers.MicroDownloader.downloader as downloadDb
from env_file import env_varz


if __name__ == "__main__":
    print('starting go download batch...')

    env_varz.init_argz()

    
    ############
    # CLI ARGS #
    ############
    if env_varz.dwn_query_todo == True:    # $ python .\kickDownloader.py --query-todo
        print("env_varz.dwn_query_todo:", env_varz.dwn_query_todo)
        downloadDb.getTodoFromDatabase(0, False)
        exit(0)

    ##############
    # GO BABY GO #
    ##############
    start_time = time.time()
    isDebug=False
    downloadGo.goDownloadBatch(isDebug)

    elapsed_time = time.time() - start_time

    print('Finished kickDownloader')
    print("-------------------")
    print("Total time: ", str(int(elapsed_time)))
    print("-------------------")