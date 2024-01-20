import controllers.MicroDownloader.downloaderGo as downloadGo

if __name__ == "__main__":
    print('starting go download batch...')
    x = downloadGo.goDownloadBatch(isDebug=False)
    print('Finished kickDownloader')