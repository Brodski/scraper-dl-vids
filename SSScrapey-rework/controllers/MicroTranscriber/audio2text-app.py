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
      
      # for filename in saved_caption_files: # [vodx.json, vodx.vtt]
      #   s3_file_location = uploadCaptionsToS3(filename, todo)
      try:
        cleanUpFiles(audio_name_encode)
      except:
         print('failed to run cleanUpFiles() on: ' + audio_name_encode)
    print("done!!")
    print("done!!")
    print("done!!")
    print("done!!")
    print("done!!")
    