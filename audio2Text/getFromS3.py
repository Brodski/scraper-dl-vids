import json
import requests
import urllib.request
import urllib.parse
import os
import time
import boto3
import gogoWhisperFAST
import langcodes

import env_app as env_varz

def _getCompletedJsonS3():
    s3 = boto3.client('s3')

    print (env_varz.S3_COMPLETED_AUDIO_UPLOADED)
    print (env_varz.S3_COMPLETED_AUDIO_UPLOADED)
    print (env_varz.S3_COMPLETED_AUDIO_UPLOADED)
    
    
    try:
      resAudio = s3.get_object(Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_AUDIO_UPLOADED)
      audio_dict = json.loads(resAudio["Body"].read().decode("utf-8")) if resAudio != None else {}
    except:
      print("error: completed-audio json file does not exist. There is no audio to download?")
      return
    try:
      resCaps = s3.get_object(Bucket=env_varz.BUCKET_NAME, Key=env_varz.S3_COMPLETED_CAPTIONS_UPLOADED)
      caps_dict =  json.loads(resCaps["Body"].read().decode("utf-8")) if resCaps != None else {}
    except:
      caps_dict = {}
      print("error: completed-captions json file does not exist")
      # return
    
    print("audio_dict")
    print(audio_dict)
    print(type(audio_dict))
    print()
    print("caps_dict")
    print(caps_dict)
    print()
    print(audio_dict.get('poopy'))
    print(audio_dict.get('poopy'))
    print(audio_dict.get('poopy'))

    todo_list = {}
    for k_channel, v_audio_list in audio_dict.items():
      print(k_channel + ": " + str(v_audio_list))
      print(caps_dict.get(k_channel))
      if caps_dict.get(k_channel):
        channel_caps_list = set( caps_dict.get(k_channel) ) # using a set is apparently faster
        incomplete_caps = [audio_id for audio_id in v_audio_list if audio_id not in channel_caps_list]
        todo_list[k_channel] = incomplete_caps
        print (incomplete_caps)
      else:
         todo_list[k_channel] = v_audio_list
    print("+++++++++++++++++++++++++")
    print("+++++++++++++++++++++++++")
    print("+++++++++++++++++++++++++")
    print(todo_list)
    return todo_list



def uploadCaptionsToS3(filename, channel, vod_id):
    print ("XXXXXXXXXXXXXX                      XXXXXXXXXXXXXX")
    print ("XXXXXXXXXXXXXX  uploadCaptionsToS3  XXXXXXXXXXXXXX")
    print ("XXXXXXXXXXXXXX                      XXXXXXXXXXXXXX")
    print()

    s3 = boto3.client('s3')
    file_abs = os.path.abspath(env_varz.A2T_ASSETS_CAPTIONS + filename)
    # filename is encoded.
    filename = urllib.parse.unquote(filename)
    print("decoded")
    print(filename)
    s3CapFileKey = env_varz.S3_CAPTIONS_KEYBASE + channel + "/" + vod_id + "/" + filename

    
    print("channel: " + channel)  
    print("vod_id: " + vod_id) 
    print("filename: " + filename) 
    print("filen: " + file_abs)
    print("s3CapFileKey: " + s3CapFileKey)
    try:
      s3.upload_file(file_abs, env_varz.BUCKET_NAME, s3CapFileKey)
      return True
    except:
      print("oops! failed to upload: " + filename)
      return False

def get_language_code(full_language_name):
    try:
        language_code = langcodes.find(full_language_name).language
        return language_code
    except langcodes.LanguageNotFoundError:
        return None


def downloadAudio(link_path_todo):
  print("######################################")
  print("             downloadAudio            ")
  print("######################################")
  for i, link_path_todo in enumerate(todo_list):
    print(i)
    print("link_path_todo: " + str(link_path_todo))
    continue
    audio_url = env_varz.S3_DOMAIN_WGET + link_path_todo
    audio_name = os.path.basename(audio_url) # A trick to get the file name. eg) filename = "Calculated-v5057810.mp3"
    audio_name_decode = urllib.parse.quote(audio_name)
    # print("audio_url BEFORE=" +audio_url)
    meta_url = audio_url.replace(audio_name, "metadata.json")
    audio_url = audio_url.replace(audio_name, audio_name_decode)    
    # meta_url = audio_url.replace(audio_name, "metadata.json")
    relative_filename = env_varz.A2T_ASSETS_AUDIO +  audio_name_decode
    print("audio_name_decode=" +audio_name_decode)
    print("audio_name=" +audio_name)
    print()
    print("audio_url=" +audio_url)
    print("meta_url=" +meta_url)
    print()
    print("relative_filename=" + relative_filename)
    # exit()
    # Audio file download locally
    local_filename  = urllib.request.urlretrieve(audio_url, relative_filename)

    # Metadata.json get in memory
    response_meta = urllib.request.urlopen(meta_url)

    data = response_meta.read()
    json_data = json.loads(data)
    print()
    print()
    print("      json_data")
    # print(json_data)
    print ("    " + json_data["channel"])
    print ("    " + json_data["link"])
    print ("    " + json_data["link"].split("/")[-1])
    print ("    " + json_data["language"])
    # print (json_data["url"])
    print("local_filename")
    print(local_filename)

    absolute_path = os.path.abspath(relative_filename)

    print ("+++++++++++++++++++++++++++++++++++")
    print ("link_path_todo: " + link_path_todo)
    print ("os-base: " + audio_name_decode)
    print ("os-relative_filename: " + relative_filename)
    print("Absolute path:", absolute_path)
    # print ("headers" )
    # print (headers )
    # print ("local_filename" )
    # print (local_filename )
    # print ("ass" )
    # print (ass )

    language_code = get_language_code(json_data["language"])
    saved_caption_files = gogoWhisperFAST.run(model_size="base", filename=audio_name_decode)

    for filename in saved_caption_files: # [vodx.json, vodx.vtt]
        uploadCaptionsToS3(filename, json_data["channel"], json_data["link"].split("/")[-1])
    


if __name__ == '__main__':
  todo_dict = _getCompletedJsonS3()
  # todo_list =  ['channels/vod-audio/lck/576354726/Clip%3A+AF+vs.+KT+-+SB+vs.+DWG+%5B2020+LCK+Spring+Split%5D-v576354726.mp3', 'channels/vod-audio/lolgeranimo/28138895/The+Geraniproject%21+I+Love+You+Guys%21%21%21-v28138895.mp3', 'channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3']
  print("##########")
  todo_list = []
  for k_chan,v_vods in todo_dict.items():
     for vod in v_vods:
        print(k_chan)
        print(vod)
        # print(urllib.parse.quote(vod))
        todo_list.append(env_varz.S3_CAPTIONS_KEYBASE + k_chan + "/" + urllib.parse.quote(str(vod)))
  print()
  print("todo_dict")
  print(todo_dict)
  print()
  print("todo_list")
  print(todo_list)
  print()
  print()
  downloadAudio(todo_list)

