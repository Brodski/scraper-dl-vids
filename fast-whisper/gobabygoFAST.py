# from faster_whisper import WhisperModel
import os
import time
import faster_whisper
import faster_whisper.utils
# import torch

# from faster_whisper.utils import get_writer

# http://muzso.hu/2015/04/25/how-to-speed-up-slow-down-an-audio-stream-with-ffmpeg
# https://gist.github.com/frankrausch/f871b573060b4d0cf34a7d86077e433f
# 
# $ ffmpeg -i .\BarbaraWaltersFAST.mp3 -filter:a "atempo=1.5" "BarbaWaltersFASTER.mp3"
# $ ffmpeg -i .\BarbaraWaltersFAST.mp3 -filter:a "atempo=1.5" "BarbaWaltersFASTER.mp3"
# $ ffmpeg -i .\BarbaraWaltersFAST.mp3 -filter:a "atempo=1.5" "BarbaWaltersFASTER.mp3"
# $ ffmpeg -i .\BarbaraWaltersFAST.mp3 -filter:a "atempo=1.5" "BarbaWaltersFASTER.mp3"
# $ ffmpeg -i .\BarbaraWaltersFAST.mp3 -filter:a "atempo=1.5" "BarbaWaltersFASTER.mp3" 

# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")

filename = "BarbaraWalters.mp3"
asset_dir = "assets/raw/"
model_size = "large-v2"
# model_size = "medium"
model_size = "small"

model = faster_whisper.WhisperModel(model_size, compute_type="int8")
model = faster_whisper.WhisperModel(model_size, compute_type="int8",  cpu_threads=16) # 4 default
# filename = "Bootcamp to Challenger ｜-v1747933567.f_Audio_Only.mp3"
# filename = "BarbaraWalters.mp3"
# filename = "BarbaWaltersFASTER.mp3"
filename = "bootcampFAST.mp3"
audio_path = asset_dir + filename

# bootcampFAST
# @Small @4  threads ---> 38.72 min
# @small @16 threads ---> 34.03 min


# Bootcamp to Challenger ｜-v1747933567.f_Audio_Only.mp3
# bootchamp-LONG @small @4 threads--->  38.33 MINUTES
# bootchamp-LONG @small @4 threads--->  92.82 MINUTES


# BarbaraWalters
# small = 30.654762506484985
# med = 71.45487022399902
# v2 = 179.35309767723083

start_time = time.time()
segments, info = model.transcribe(audio_path, language="en")

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

end_time = time.time() - start_time

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
print()
print("run time =" + str(end_time))
print()
print("Completed: " + audio_path)
