import whisper
import whisper.utils
from whisper.utils import get_writer

import os 
# from whisper import cli

model = whisper.load_model("base")
result = model.transcribe("BarbaraWalters.mp3",  fp16=False)

# model.utils.write_vtt("BarbaraWalters.mp3", "BarbaraWalters.vtt")
# whisper.utils.write_vtt("BarbaraWalters.mp3", "BarbaraWalters.vtt")

output_dir = "."
audio_path="BarbaraWalters.mp3"
audio_basename = os.path.basename(audio_path)

print ("output_dir: ", output_dir )
print ("audio_path: ", audio_path)
print ("audio_basename: ", audio_basename)


# Save as an SRT file
srt_writer = get_writer("srt", output_dir)
srt_writer(result, audio_basename + ".srt")


# Save as a VTT file
vtt_writer = get_writer("vtt", output_dir)
vtt_writer(result, audio_basename + ".vtt")



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
print(result["text"])
print("--------------write_vtt--------------")
# print(result["segments"])
