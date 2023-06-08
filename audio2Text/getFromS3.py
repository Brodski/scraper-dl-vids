# import requests
import urllib.request
import os
import time
import boto3
import gogoWhisperFAST


# CURRENT_DATE_YMD = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

BUCKET_NAME = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket'
directory_name = 'mydirectory' # this directory legit exists in this bucket ^
directory_name_real = "channels/ranking/raw"
S3_COMPLETED_AUDIO_UPLOADED = 'channels/completed/audio/completed.json'
S3_COMPLETED_CAPTIONS_UPLOADED = 'channels/completed/captions/completed.json'
S3_ALREADY_DL_KEYBASE = 'channels/scrapped/'
S3_CAPTIONS_KEYBASE = 'channels/captions/'
# S3_ALREADY_DL_KEY = 'channels/scrapped/lolgeranimo/2023-04-01.json'
S3_DOMAIN_WGET = "https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/"
A2T_ASSETS_AUDIO = "./assets/audio/"

# url = 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/testz/BarbaraWalters.mp3'
# url_base = "https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/captions/lck/576354726/Clip%3A+AF+vs.+KT+-+SB+vs.+DWG+%5B2020+LCK+Spring+Split%5D-v576354726.mp3

# filename = os.path.basename(url)
# urllib.request.urlretrieve(url, filename)


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

    objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_CAPTIONS_KEYBASE, EncodingType="url")['Contents']
    # good use of cont token https://www.tabnine.com/code/javascript/functions/aws-sdk/ListObjectsV2Output/NextContinuationToken
    # print("ContinuationToken: " +     str(obj.get('ContinuationToken')))
    # print("NextContinuationToken: " + str(obj.get('NextContinuationToken')))
    sorted_objects = sorted(objects, key=lambda obj: obj['Key'])
    print("-----SORTED (OFFICIAL)---- ")
    todo_list = []
    for obj in sorted_objects:
        print("===============================")
        # print("Key= " + f"{obj['Key']}")
        if obj['Key'].split('/')[-1] != "metadata.json":
          todo_list.append(obj['Key'])
          print(obj)

    print ()
    print ("todo_list:")
    print ()
    for myFile in todo_list:
       print(myFile)
    
    return todo_list


if __name__ == '__main__':
  # todo_list = _getUploadedFilesS3()
  todo_list =  ['channels/captions/lck/576354726/Clip%3A+AF+vs.+KT+-+SB+vs.+DWG+%5B2020+LCK+Spring+Split%5D-v576354726.mp3', 'channels/captions/lolgeranimo/28138895/The+Geraniproject%21+I+Love+You+Guys%21%21%21-v28138895.mp3', 'channels/captions/lolgeranimo/5057810/Calculated-v5057810.mp3']
  print()
  print()
  print(todo_list)
  print()
  print()
  print("######################################")
  print("             GET FROM S3              ")
  print("######################################")
  for i, todo in enumerate(todo_list):
    print(i)
    print("file: " + todo)
    link_path = todo
    link_url = S3_DOMAIN_WGET + link_path
    filename = os.path.basename(link_url) # A trick to get the file name. eg) filename = "Calculated-v5057810.mp3"
    relative_filename = A2T_ASSETS_AUDIO +  filename
    ass = urllib.request.urlretrieve(link_url, relative_filename)
     
    # current_dir = os.getcwd()
    absolute_path = os.path.abspath(relative_filename)


    print ("+++++++++++++++++++++++++++++++++++")
    print ("link_path: " + link_path)
    print ("os-base: " + filename)
    print ("os-relative_filename: " + relative_filename)
    print("Absolute path:", absolute_path)
    print ("ass" )
    print (ass)

    gogoWhisperFAST.run(model_size="base", filename=filename)