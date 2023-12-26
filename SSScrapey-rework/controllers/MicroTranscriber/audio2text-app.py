import json
import requests
import urllib.request
import urllib.parse
import os
import time
import boto3
import gogoWhisperFAST
import langcodes
from Todo_model import Todo

from typing import List
import env_file as env_varz
# import env_app as env_varz


# returns -> [
#   {
#     "channel": "lolgeranimo",
#     "id": "1853780899",
#     "title": "Some_Jungle_then_Adc_Academy_later-v1853780899.mp3",
#     "link_s3": "https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/1853780899/Some_Jungle_then_Adc_Academy_later-v1853780899.mp3"
#   },
# ]
def _getCompletedJsonS3():
    s3 = boto3.client('s3')
    print("env_varz.S3_COMPLETED_TODO_AUDIO")
    print("env_varz.S3_COMPLETED_TODO_AUDIO")
    print("env_varz.S3_COMPLETED_TODO_AUDIO")
    print(env_varz.S3_COMPLETED_TODO_AUDIO)
    print('os.getenv("AWS_SECRET_ACCESS_KEY")')
    print('os.getenv("AWS_SECRET_ACCESS_KEY")')
    print('os.getenv("AWS_SECRET_ACCESS_KEY")')
    # print(os.getenv("AWS_SECRET_ACCESS_KEY"))
    # print(os.getenv("MY_AWS_ACCESS_KEY_ID"))
    try:
      print("GO!zzz")
      resAudio = s3.get_object(Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_TODO_AUDIO)
      print("resAudio")
      print(resAudio)
      todo_list_pre = json.loads(resAudio["Body"].read().decode("utf-8")) if resAudio != None else {}
    except:
      print("error: completed-audio json file does not exist. There is no audio to download?")
      return
    todo_list = []
    for todo in todo_list_pre:
       print(todo)
       todo = Todo(channel=todo.get("channel"), id=todo.get("id"), title=todo.get("title"), link_s3=todo.get("link_s3") )
       todo_list.append(todo)
    for todo in todo_list_pre:
       print(todo['channel'] + " : " + todo['title'])
    return todo_list



def uploadCaptionsToS3(filename, todo: Todo):
    print ("XXXXXXXXXXXXXX                      XXXXXXXXXXXXXX")
    print ("XXXXXXXXXXXXXX  uploadCaptionsToS3  XXXXXXXXXXXXXX")
    print ("XXXXXXXXXXXXXX                      XXXXXXXXXXXXXX")
    print()

    file_abs = os.path.abspath(env_varz.A2T_ASSETS_CAPTIONS + filename)
    # filename is encoded.
    filename = urllib.parse.unquote(filename)
    print("filename: " + str(filename))
    print("todo:")
    print(json.dumps(todo, default=lambda o: o.__dict__, indent=4))
    s3CapFileKey = env_varz.S3_CAPTIONS_KEYBASE + todo.channel + "/" + todo.id + "/" + filename

    print("channel: " + todo.channel)  
    print("vod_id: " + todo.id) 
    print("filename: " + filename) 
    print("file_abs: " + file_abs)
    print("s3CapFileKey: " + s3CapFileKey)
    s3 = boto3.client('s3')
    try:
      content_type = ''
      if file_abs[-4:] == '.txt':
        content_type = 'text/plain; charset=utf-8'
      if file_abs[-5:] ==  '.json':
        content_type = 'application/json; charset=utf-8'
      if file_abs[-4:] ==  '.vtt':
        content_type = 'text/vtt; charset=utf-8'
      s3.upload_file(file_abs, env_varz.BUCKET_NAME, s3CapFileKey, ExtraArgs={ 'ContentType': content_type })
      return s3CapFileKey # channels/vod-audio/lolgeranimo/1856310873/How_to_Climb_on_Adc_So_washed_up_i_m_clean_-_hellofresh-v1856310873.vtt
    except:
      print("oops! failed to upload: " + filename)
      return False

def get_language_code(full_language_name):
    try:
        language_code = langcodes.find(full_language_name).language
        return language_code
    except:
        return None


def downloadAudio(todo: Todo):
  print("######################################")
  print("             downloadAudio            ")
  print("######################################")
  print("link_path_todo: " + str(todo))
  audio_url = todo.link_s3
  print("")
  print("")
  print("")
  print("audio_url before=" + str(audio_url))

  audio_name = os.path.basename(audio_url) # A trick to get the file name. eg) filename = "Calculated-v5057810.mp3"
  audio_name_encode = urllib.parse.quote(audio_name)
  meta_url = audio_url.replace(audio_name, "metadata.json")
  audio_url = audio_url.replace(audio_name, audio_name_encode)    
  relative_filename = env_varz.A2T_ASSETS_AUDIO +  audio_name_encode

  print("audio_url=" + str(audio_url))
  print("audio_name=" + str(audio_name))
  print("audio_name_encode=" + str(audio_name_encode))
  print("meta_url=" + str(meta_url))
  print("relative_filename=" + str(relative_filename))    

  # Audio file download locally
  local_filename  = urllib.request.urlretrieve(audio_url, relative_filename) # audio_url = Calculated-v123123.ogg
  print("local_filename")
  print(local_filename)
  print(local_filename)
  print(local_filename)
  print(local_filename)
  print(local_filename)
  # Metadata.json get in memory
  response_meta = urllib.request.urlopen(meta_url)
  data = response_meta.read()
  metadata_file_s3 = json.loads(data)

  return audio_name_encode, metadata_file_s3

def cleanUpFiles(filename):
   
  file_abs = os.path.abspath(env_varz.A2T_ASSETS_AUDIO + filename)
  print("cleanUpFiles - file_abs= " + file_abs)
  print("cleanUpFiles - file_abs= " + file_abs)
  print("cleanUpFiles - file_abs= " + file_abs)
  if os.getenv("ENV") != "local":
     print("DELETING IT!!!!!!!")
     os.remove(file_abs)
  return 

def doWhisperStuff(audio_name_encode, metadata_file_s3):
    lang_code = get_language_code(metadata_file_s3["language"])
    print()
    print()
    print("      metadata_file_s3")
    print("    " + metadata_file_s3["channel"])
    print("    " + metadata_file_s3["link"])
    print("    " + metadata_file_s3["language"])
    print("    " + str(lang_code))
    print("    " + "audio_name_encode=" + audio_name_encode)
    model = (env_varz.WHSP_MODEL_SIZE + ".en") if lang_code == "en" else env_varz.WHSP_MODEL_SIZE
    saved_caption_files = gogoWhisperFAST.run(model_size=model, lang_code=lang_code, filename=audio_name_encode)
    return saved_caption_files

# todo_list
# {
#     "channel": "lolgeranimo",
#     "id": "1853780899",
#     "title": "Some_Jungle_then_Adc_Academy_later-v1853780899.mp3",
#     "link_s3": "https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/1853780899/Some_Jungle_then_Adc_Academy_later-v1853780899.mp3"
# }
# {
#     "channel": "lolgeranimo",
#     "id": "1856310873",
#     "title": "How_to_Climb_on_Adc_So_washed_up_i_m_clean_-_hellofresh-v1856310873.mp3",
#     "link_s3": "https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/1856310873/How_to_Climb_on_Adc_So_washed_up_i_m_clean_-_hellofresh-v1856310873.mp3"
# } 
if __name__ == '__main__':
    isDebug = env_varz.IS_DEBUG
    super_start = time.time()
    print('Start')
    print(os.getenv("ENV"))
    todo_list = _getCompletedJsonS3() 
    if isDebug and os.getenv("ENV") == "local":
      todo = Todo(channel="lolgeranimo", id="28138895", title="The Geraniproject! I Love You Guys!!!-v28138895", link_s3="https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/28138895/The_Geraniproject_I_Love_You_Guys-v28138895.mp3" )
      todo2 = Todo(channel="lolgeranimo", id="5057810", title="Calculated-v5057810", link_s3="https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3" )
      todo_list = [todo, todo2]

    print("###############")
    for todo in todo_list:
      print("---")
      print(json.dumps(todo, default=lambda o:o.__dict__, indent=4))
      audio_name_encode, metadata_file_s3 = downloadAudio(todo)
      saved_caption_files = doWhisperStuff(audio_name_encode, metadata_file_s3)
      
      for filename in saved_caption_files: # [vodx.json, vodx.vtt]
        s3_file_location = uploadCaptionsToS3(filename, todo)
      try:
        cleanUpFiles(audio_name_encode)
      except:
         print('failed to run cleanUpFiles() on: ' + audio_name_encode)
    print("done!!")
    print("done!!")
    print("done!!")
    print("done!!")
    print("done!!")
    
    # end = time.time() - super_start
    # some_obj = {
    #     "time": end,
    #     "s3_file_location": s3_file_location
    # }
    # s3 = boto3.client('s3')
    # s3.put_object(Body=json.dumps(some_obj, default=lambda o: o.__dict__), Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_CAPTIONS_DONE)

