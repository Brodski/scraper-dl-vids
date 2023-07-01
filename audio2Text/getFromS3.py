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
import env_app as env_varz

def _getCompletedJsonS3():
    s3 = boto3.client('s3')
    print (env_varz.S3_COMPLETED_AUDIO_UPLOADED)
    print (env_varz.S3_COMPLETED_AUDIO_UPLOADED)
    print (env_varz.S3_COMPLETED_AUDIO_UPLOADED)

    try:
      resAudio = s3.get_object(Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_TODO_AUDIO)
      todo_list_pre = json.loads(resAudio["Body"].read().decode("utf-8")) if resAudio != None else {}
      # returns -> [
      #   {
      #     "channel": "lolgeranimo",
      #     "id": "1853780899",
      #     "title": "Some_Jungle_then_Adc_Academy_later-v1853780899.mp3",
      #     "link_s3": "https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/1853780899/Some_Jungle_then_Adc_Academy_later-v1853780899.mp3"
      #   },
      # ]
    except:
      print("error: completed-audio json file does not exist. There is no audio to download?")
      return
    todo_list = []
    for todo in todo_list_pre:
       print(todo)
      #  print(todo.__dict__)
       todo = Todo(channel=todo.get("channel"), id=todo.get("id"), title=todo.get("title"), link_s3=todo.get("link_s3") )
       todo_list.append(todo)
    return todo_list



def uploadCaptionsToS3(filename, todo: Todo):
    print ("XXXXXXXXXXXXXX                      XXXXXXXXXXXXXX")
    print ("XXXXXXXXXXXXXX  uploadCaptionsToS3  XXXXXXXXXXXXXX")
    print ("XXXXXXXXXXXXXX                      XXXXXXXXXXXXXX")
    print()

    file_abs = os.path.abspath(env_varz.A2T_ASSETS_CAPTIONS + filename)
    # filename is encoded.
    filename = urllib.parse.unquote(filename)
    print("decoded")
    print(filename)
    print('dump todo')
    print('dump todo')
    print('dump todo')
    print(json.dumps(todo, default=lambda o: o.__dict__, indent=4))
    s3CapFileKey = env_varz.S3_CAPTIONS_KEYBASE + todo.channel + "/" + todo.id + "/" + filename

    
    print("channel: " + todo.channel)  
    print("vod_id: " + todo.id) 
    print("filename: " + filename) 
    print("file_abs: " + file_abs)
    print("s3CapFileKey: " + s3CapFileKey)
    s3 = boto3.client('s3')
    try:
      s3.upload_file(file_abs, env_varz.BUCKET_NAME, s3CapFileKey)
      return s3CapFileKey # channels/vod-audio/lolgeranimo/1856310873/How_to_Climb_on_Adc_So_washed_up_i_m_clean_-_hellofresh-v1856310873.vtt
    except:
      print("oops! failed to upload: " + filename)
      return False

def get_language_code(full_language_name):
    try:
        language_code = langcodes.find(full_language_name).language
        return language_code
    except langcodes.LanguageNotFoundError:
        return None


def downloadAudio(todo_list: List[Todo]):
  print("######################################")
  print("             downloadAudio            ")
  print("######################################")
  for todo in todo_list:
    print("-----------------------------------")
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
    local_filename  = urllib.request.urlretrieve(audio_url, relative_filename)

    # Metadata.json get in memory
    response_meta = urllib.request.urlopen(meta_url)

    data = response_meta.read()
    json_data = json.loads(data)

    lang_code = get_language_code(json_data["language"])
    print()
    print()
    print("      json_data")
    print("    " + json_data["channel"])
    print("    " + json_data["link"])
    print("    " + json_data["language"])
    print("    " + str(lang_code))
    print("    " + "audio_name_encode=" + audio_name_encode)
    # print (json_data["url"])
    print("local_filename")
    print(local_filename)
    saved_caption_files = gogoWhisperFAST.run(model_size="base", lang_code=lang_code, filename=audio_name_encode)

    for filename in saved_caption_files: # [vodx.json, vodx.vtt]
      # uploadCaptionsToS3(filename, json_data["channel"], json_data["link"].split("/")[-1])
      s3_file_location = uploadCaptionsToS3(filename, todo)
    return s3_file_location
    # if s3_file_location:
    #    updateCompletedCaptionsS3(s3_file_location, todo)
    
# # THIS IS PRACTICALLY COPY PASTED FROM mainController.js
# def updateCompletedCaptionsS3(s3_file_location, todo: Todo):
#     allOfIt = _getAllCompletedJsonSuperS3__BETTER()
#     print("allOfIt")
#     print(allOfIt)
#     print()
#     print()
#     print()
#     print(json.dumps(allOfIt.__dict__, default=lambda o: o.__dict__))
#     if allOfIt is None or len(allOfIt)==0:
#         raise Exception("Something is wrong with '_getCompletedAudioJsonSuperS3' audio json file")
#     captions_ext = ['.json', '.vtt']
#     missing_captions_list = []

#     for k_chn, v_id_files in allOfIt.items():
#         print(k_chn)
#         for id, files in v_id_files.items():
#             # print ()
#             # print ("    " + str(id))
#             # print ("    " + str(files))
#             # hasAudio = False
#             hasCaptions = False
#             for file in files:
#                 if file == "metadata.json":
#                     continue
#                 if file[-5:] not in captions_ext and file[-4:] not in captions_ext:
#                     hasAudio = True
#                     vod_title = file
#                     continue
#                 if file[-5:] in captions_ext or file[-4:] in captions_ext:
#                     hasCaptions = True
#             if hasAudio and not hasCaptions:
#                 print("MISSING CAPTIONS for: " + k_chn + " " + id)
#                 print()
#                 vod = Vod(channel=k_chn, id=id, title=urllib.parse.unquote(vod_title))
#                 vod_encode = urllib.parse.quote(vod.title)
#                 vod_path = env_varz.S3_CAPTIONS_KEYBASE + vod.channel + "/" + vod.id + "/" + vod_encode
#                 vod.link_s3 =  env_varz.BUCKET_DOMAIN + "/" + vod_path

#                 missing_captions_list.append(vod)
#     s3 = boto3.client('s3')
#     s3.put_object(Body=json.dumps(missing_captions_list, default=lambda o: o.__dict__), Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_TODO_AUDIO)
#     print ("MISSSING!")
#     print ("MISSSING!")
#     print ("MISSSING!")
#     print ("MISSSING!")
#     print (missing_captions_list)
#     print (json.dumps(missing_captions_list, default=lambda o: o.__dict__, indent=4))
#     if isDebug:
#         return json.loads(json.dumps(missing_captions_list, default=lambda o: o.__dict__)) 
#     return missing_captions_list





# COPY AND PASTED CODE FROM mainController (b/c they are 2 differents servers)
# COPY AND PASTED CODE FROM mainController (b/c they are 2 differents servers)
def _getAllCompletedJsonSuperS3__BETTER(): # -> mocks/completedJsonSuperS3.py
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket=env_varz.BUCKET_NAME, Prefix=env_varz.S3_CAPTIONS_KEYBASE)['Contents']
    sorted_objects = sorted(objects, key=lambda obj: obj['Key'])
    print("----- _getCompletedAudioJsonSuperS3 ---- ")
    
    allOfIt = {}
    for obj in sorted_objects:
        filename = obj['Key'].split("/")[4:][0]
        vod_id = obj['Key'].split("/")[3:4][0]
        channel = obj['Key'].split("/")[2:3][0]
        print("@@@@@@@@@@@@@@@@@@@@@")
        print("Key= " + f"{obj['Key']}")
        print("channel: " +  (channel))     
        print("vod_id: " +  (vod_id))
        print("filename: " + (filename))
        # 1. obj[key] = channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3
        # 2. temp = lolgeranimo/5057810/Calculated-v5057810.mp3
        # 3. channel, vod_i, vod_title = [ lolgeranimo, 5057810, "Calculated-v5057810.mp3" ] 
        temp = str(obj['Key']).split(env_varz.S3_CAPTIONS_KEYBASE, 1)[1]   # 2
        # channel, vod_id, vod_title = temp.split("/", 2)[:3] # 3 
        if allOfIt.get(channel):
            if allOfIt.get(channel).get(vod_id): # if vod_id for channel exists
                allOfIt.get(channel).get(vod_id).append(filename)
            else: # else create a list that has all filenames
                allOfIt.get(channel)[vod_id] = [filename]
        else:
            vod_dict = { vod_id: [filename] }
            allOfIt[channel] = vod_dict
    print ()
    print ("(_getAllCompletedJsonSuperS3__BETTER) allOfIt=")
    print (json.dumps(allOfIt, default=lambda o: o.__dict__, indent=4))
    print ()
    # for key, value in allOfIt.items():
    #     print(key + ": " + str(value))
    return allOfIt


    
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

  # "lolgeranimo": {
  #   "28138895": [
  #     "The Geraniproject! I Love You Guys!!!-v28138895.json",
  #     "The Geraniproject! I Love You Guys!!!-v28138895.mp3",
  #     "The Geraniproject! I Love You Guys!!!-v28138895.vtt",
  #     "metadata.json"
  #   ],
if __name__ == '__main__':
  super_start = time.time()
  print('hello')
  todo_list = _getCompletedJsonS3() 
  print("##########")
  print("todo_listzzzz")
  print(todo_list)
  todo = Todo(channel="lolgeranimo", id="28138895", title="The Geraniproject! I Love You Guys!!!-v28138895", link_s3="https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/28138895/The_Geraniproject_I_Love_You_Guys-v28138895.mp3" )
  todo_list = [todo]
  print()
  print('asdasda')
  for todo in todo_list:
    print(json.dumps(todo, default=lambda o:o.__dict__, indent=4))
  print()
  s3_file_location = downloadAudio(todo_list)
  end = time.time() - super_start
  some_obj = {
     "time": end,
     "s3_file_location": s3_file_location
  }
  s3 = boto3.client('s3')
  s3.put_object(Body=json.dumps(some_obj, default=lambda o: o.__dict__), Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_CAPTIONS_DONE)

