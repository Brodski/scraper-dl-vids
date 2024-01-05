import controllers.MicroDownloader.go as downloadGo

if __name__ == "__main__":
    x = downloadGo.goDownloadBatch(isDebug=False)
    print('Finished kickDownloader')