import faster_whisper
# import whisper.utils
from whisper.utils import get_writer

import os
import time
import torch


main_dir = r'C:/Users/BrodskiTheGreat/Desktop/desktop/Code/scraper-dl-vids'
#main_dir = r'/home/ssm-user/scraper-dl-vids'
asset_dir = "assets/audio"
# model_size = "large-v2"
model_size = "medium"
# model_size = "small"
# model_size = "tiny"

print("torch.cuda.is_available(): " + str(torch.cuda.is_available()))


# filename = "Bootcamp to Challenger - Gaming-v1767827635.f_Audio_Only.mp4"
# filename = "Bootcamp to Challenger - Gaming-v1767827635.f_Audio_Only.mp3"
# filename = "Bootcamp to Challenger ｜-v1747933567.f_Audio_Only-wtf.mp3"
filename = "BarbaraWalters.mp3"
filename = "OPENASSISTANT TAKES ON CHATGPT!-TFa539R09EQ-fast.mp3"
#filename = "Adc+Academy+-+Informative+Adc+Stream+-+GrandMaster+today？+[v1792628012].mp3"
asset_dir = "assets/audio/"
output_dir = "./assets/output"
audio_basename = os.path.basename(asset_dir + filename)


# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")
# model = faster_whisper.WhisperModel(model_size, compute_type="int8")
#model = faster_whisper.WhisperModel(model_size, device="cuda", compute_type="int8",  cpu_threads=8) # 4 default
model = faster_whisper.WhisperModel(model_size, device="cuda", compute_type="int8", cpu_threads=8) # 4 default
audio_path = "{}/{}/{}".format(main_dir, asset_dir, filename)

start_time = time.time()
print("start!")
# segments, info = model.transcribe(audio_path, language="en", condition_on_previous_text=False, beam_size=2, best_of=2)
# segments, info = model.transcribe(audio_path, language="en", condition_on_previous_text=False, vad_filter=True)
segments, info = model.transcribe(audio_path, language="en", condition_on_previous_text=False, vad_filter=True, beam_size=2, best_of=2)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

result = {
    "segments": []
}

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    result["segments"].append({
        "start" : segment.start,
        "end" :   segment.end,
        "text" :  segment.text,
    })

end_time = time.time() - start_time
srt_writer = get_writer("srt", output_dir)
srt_writer(result, audio_basename + ".srt")


print("========================================")
print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
print()
print("run time =" + str(end_time))
print()
print("Completed srt: " +  audio_basename + ".srt")
print("Completed: " + audio_path)