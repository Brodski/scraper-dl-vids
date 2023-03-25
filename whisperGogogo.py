import whisper
import whisper.utils
import os 
# from whisper import cli

model = whisper.load_model("base")
result = model.transcribe("BarbaraWalters.mp3")

# model.utils.write_vtt("BarbaraWalters.mp3", "BarbaraWalters.vtt")
# whisper.utils.write_vtt("BarbaraWalters.mp3", "BarbaraWalters.vtt")

output_dir = "."
audio_path="BarbaraWalters.mp3"
audio_basename = os.path.basename(audio_path)

print ("output_dir: ", output_dir )
print ("audio_path: ", audio_path)
print ("audio_basename: ", audio_basename)

# from whisper.utils import write_srt
# save VTT
with open(os.path.join(output_dir, audio_basename + ".vtt"), "w", encoding="utf-8") as vtt:
    whisper.utils.write_vtt(result["segments"], file=vtt)

# save SRT
with open(os.path.join(output_dir, audio_basename + ".srt"), "w", encoding="utf-8") as srt:
    whisper.utils.write_srt(result["segments"], file=srt)

# save TXT
with open(os.path.join(output_dir, audio_basename + ".txt"), "w", encoding="utf-8") as txt:
    whisper.utils.write_txt(result["segments"], file=txt)

# whisper.utils.write_vtt(result["segments"], file="BarbaraWalters.vtt")
print(result["text"])
print("--------------write_vtt--------------")
# print(result["segments"])
