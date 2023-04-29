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

main_dir = r'C:/Users/BrodskiTheGreat/Desktop/desktop/Code/scraper-dl-vids'
asset_dir = "assets\\raw"
# model_size = "large-v2"
# model_size = "medium"
model_size = "small"
# C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\fast-whisper\assets\raw

# C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\fast-whisper
model = faster_whisper.WhisperModel(model_size, compute_type="int8")
model = faster_whisper.WhisperModel(model_size, compute_type="int8",  cpu_threads=16) # 4 default
# filename = "Bootcamp to Challenger ｜-v1747933567.f_Audio_Only.mp3"
# filename = "BarbaraWalters.mp3"
# filename = "BarbaWaltersFASTER.mp3"
# filename = "bootcampFAST.mp3"
print('going 1')
filename = "Adc academy ｜ How to climb on Adc - Grandmaster Climb --v1802413591.mp3"
output_full_dir = "{}/{}/{}".format(main_dir, asset_dir, filename)
audio_path = asset_dir + filename
audio_path = output_full_dir
print('going 2')
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
print('going 3')
segments, info = model.transcribe(audio_path, language="en")
print('going 4')

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

end_time = time.time() - start_time

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
print()
print("run time =" + str(end_time))
print()
print("Completed: " + audio_path)
