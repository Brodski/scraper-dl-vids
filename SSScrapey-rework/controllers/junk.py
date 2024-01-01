
# # Expected S3 query:
# # Key= channels/vod-audio/lck/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.json
# # Key= channels/vod-audio/lck/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.mp3
# # Key= channels/vod-audio/lck/576354726/Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.vtt
# # Key= channels/vod-audio/lck/576354726/metadata.json
# # Key= channels/vod-audio/lolgeranimo/28138895/The Geraniproject! I Love You Guys!!!-v28138895.json
# # Key= channels/vod-audio/lolgeranimo/28138895/The Geraniproject! I Love You Guys!!!-v28138895.mp3
# # Key= channels/vod-audio/lolgeranimo/28138895/The Geraniproject! I Love You Guys!!!-v28138895.vtt
# # Key= channels/vod-audio/lolgeranimo/28138895/metadata.json
# # Key= channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.json
# # Key= channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3
# # Key= channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.vtt
# # Key= channels/vod-audio/lolgeranimo/5057810/metadata.json
# # return = 
# # {
# #   "lck": {
# #              "28138895": ["Geraniproject.json", "Geraniproject.mp3", "Geraniproject.vtt"],
# #              "5057810": ["Calculated.json", "Calculated.mp3", "Calculated.vtt"],
# #          }
# #   "lolgeranimo" ... 
# # }
# def _getAllCompletedJsonSuperS3__BETTER(): # -> mocks/getAllCompletedJsonSuperS3__BETTER.py
#     s3 = boto3.client('s3')
#     objects = s3.list_objects_v2(Bucket=env_varz.BUCKET_NAME, Prefix=env_varz.S3_CAPTIONS_KEYBASE)['Contents']
#     sorted_objects = sorted(objects, key=lambda obj: obj['Key'])
#     print("----- _getCompletedAudioJsonSuperS3 ---- ")
    
#     allOfIt = {}
#     for obj in sorted_objects:
#         filename = obj['Key'].split("/")[4:][0]
#         vod_id = obj['Key'].split("/")[3:4][0]
#         channel = obj['Key'].split("/")[2:3][0]
#         # print("@@@@@@@@@@@@@@@@@@@@@")
#         # print("Key= " + f"{obj['Key']}")
#         # print("channel: " +  (channel))     
#         # print("vod_id: " +  (vod_id))
#         # print("filename: " + (filename))
#         # 1. obj[key] = channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.mp3
#         # 2. temp = lolgeranimo/5057810/Calculated-v5057810.mp3
#         # 3. channel, vod_i, vod_title = [ lolgeranimo, 5057810, "Calculated-v5057810.mp3" ] 
#         temp = str(obj['Key']).split(env_varz.S3_CAPTIONS_KEYBASE, 1)[1]   # 2
#         # channel, vod_id, vod_title = temp.split("/", 2)[:3] # 3 
#         if allOfIt.get(channel):
#             if allOfIt.get(channel).get(vod_id): # if vod_id for channel exists
#                 allOfIt.get(channel).get(vod_id).append(filename)
#             else: # else create a list that has all filenames
#                 allOfIt.get(channel)[vod_id] = [filename]
#         else:
#             vod_dict = { vod_id: [filename] }
#             allOfIt[channel] = vod_dict
#     print ()
#     print ("(_getAllCompletedJsonSuperS3__BETTER) allOfIt=")
#     print (json.dumps(allOfIt, default=lambda o: o.__dict__, indent=4))
#     print ()
#     # for key, value in allOfIt.items():
#     #     print(key + ": " + str(value))
#     return allOfIt




