import whisper
import whisper.utils
from whisper.utils import get_writer

import os 
import time
import torch
# from whisper import cli

# GPU STUFF (Need a fancy CUDA/Nvida gpu)
# https://stackoverflow.com/questions/75775272/cuda-and-openai-whisper-enforcing-gpu-instead-of-cpu-not-working
print ("whisper.available_models(): " + str(whisper.available_models()))
print("torch.cuda.is_available(): " + str(torch.cuda.is_available()))
# torch.cuda.init()

# filename = "Bootcamp to Challenger - Gaming-v1767827635.f_Audio_Only.mp4"
# filename = "Bootcamp to Challenger - Gaming-v1767827635.f_Audio_Only.mp3"
# filename = "Bootcamp to Challenger ｜-v1747933567.f_Audio_Only-wtf.mp3"
filename = "BarbaraWalters.mp3"
asset_dir = "assets/raw/"

# model = whisper.load_model("base")
# model = whisper.load_model("small.en")
model = whisper.load_model("small")
# model = whisper.load_model("medium")
# model = whisper.load_model("large")
# model = whisper.load_model("large-v1")
start_time = time.time()

# small = 43.8120481967926
# medium = 88.43299674987793
# medium = 82.95238137245178
# v2 =  217.49182772636414


# result = model.transcribe(filename,  fp16=False, beam_size=4, verbose = True)
# result = model.transcribe(filename, fp16=False, verbose = True)
result = model.transcribe(asset_dir + filename, verbose = True)


# model.utils.write_vtt(filename, "BarbaraWalters.vtt")
# whisper.utils.write_vtt(filename, "BarbaraWalters.vtt")

output_dir = "./assets/output"
audio_basename = os.path.basename(asset_dir + filename)

print ("output_dir: ", output_dir )
print ("filename: ", filename)
print ("audio_basename: ", audio_basename)


# Save as an SRT file
srt_writer = get_writer("srt", output_dir)
srt_writer(result, audio_basename + ".srt")


# Save as a VTT file
# vtt_writer = get_writer("vtt", output_dir)
# vtt_writer(result, audio_basename + ".vtt")


# from whisper.utils import write_srt
# save VTT
# with open(os.path.join(output_dir, audio_basename + ".vtt"), "w", encoding="utf-8") as vtt:
#     whisper.utils.WriteVTT(result["segments"])
    # whisper.utils.write_vtt(result["segments"], file=vtt)

# save SRT
# with open(os.path.join(output_dir, audio_basename + ".srt"), "w", encoding="utf-8") as srt:
#     # whisper.utils.write_srt(result["segments"], file=srt)
#     whisper.utils.WriteSRT(result["segments"], file=srt)

# # save TXT
# with open(os.path.join(output_dir, audio_basename + ".txt"), "w", encoding="utf-8") as txt:
#     # whisper.utils.write_txt(result["segments"], file=txt)
#     whisper.utils.WriteTXT(result["segments"], file=txt)

# # save JSON
# with open(os.path.join(output_dir, audio_basename + ".json"), "w", encoding="utf-8") as json:
#     # whisper.utils.write_txt(result["segments"], file=txt)
#     whisper.utils.WriteJSON(result["segments"], file=json)

# whisper.utils.write_vtt(result["segments"], file="BarbaraWalters.vtt")

end_time = time.time() 
time_diff = end_time - start_time
print("Time: "  + str(time_diff))
print("Time: "  + str(time_diff))
print("Time: "  + str(time_diff))
print("Time: "  + str(time_diff))

print(result["text"])
print("--------------write_vtt--------------")
# print(result["segments"])
