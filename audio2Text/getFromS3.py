# import requests
import urllib.request
import os
import time
import boto3



# CURRENT_DATE_YMD = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

BUCKET_NAME = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket'
directory_name = 'mydirectory' # this directory legit exists in this bucket ^
directory_name_real = "channels/ranking/raw"
S3_COMPLETED_AUDIO_UPLOADED = 'channels/completed/audio/completed.json'
S3_COMPLETED_CAPTIONS_UPLOADED = 'channels/completed/captions/completed.json'
S3_ALREADY_DL_KEYBASE = 'channels/scrapped/'
S3_CAPTIONS_KEYBASE = 'channels/captions/'
# S3_ALREADY_DL_KEY = 'channels/scrapped/lolgeranimo/2023-04-01.json'


# url = 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/testz/BarbaraWalters.mp3'

# filename = os.path.basename(url)

# start_time = time.time()

# urllib.request.urlretrieve(url, filename)

# run_time = time.time() - start_time

# print("run_time=" + str(run_time))


def _getUploadedFilesS3():
    s3 = boto3.client('s3')

    print (S3_COMPLETED_AUDIO_UPLOADED)
    print (S3_COMPLETED_AUDIO_UPLOADED)
    print (S3_COMPLETED_AUDIO_UPLOADED)
    try:
      resAudio = s3.get_object(Bucket=BUCKET_NAME, Key=S3_COMPLETED_AUDIO_UPLOADED)
    except:
      resAudio = None
      print("error: completed-audio json file does not exist. There is no audio to download?")
      return
      
    try:
      resCaps = s3.get_object(Bucket=BUCKET_NAME, Key=S3_COMPLETED_CAPTIONS_UPLOADED)
    except:
      resCaps = None
      print("Completed captions not found.")

    dataAudio = resAudio['Body'].read().decode('utf-8') if resAudio != None else {}
    dataCaps = resCaps['Body'].read().decode('utf-8') if resCaps != None else {}
    print("dataAudio")
    print(dataAudio)
    print()
    print("dataCaps")
    print(dataCaps)

    objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_CAPTIONS_KEYBASE)['Contents']
    # print("ContinuationToken: " +     str(obj.get('ContinuationToken')))
    # print("NextContinuationToken: " + str(obj.get('NextContinuationToken')))
    sorted_objects = sorted(objects, key=lambda obj: obj['Key'])
    print("-----SORTED (OFFICIAL)---- ")
    todo = []
    for obj in sorted_objects:
        print("Key= " + f"{obj['Key']}")
        if obj['Key'].split('/')[-1] != "metadata.json":
           todo.append(obj['Key'])

    print ()
    print ("todo:")
    print ()
    for myFile in todo:
       print(myFile)
    
    return todo



_getUploadedFilesS3()