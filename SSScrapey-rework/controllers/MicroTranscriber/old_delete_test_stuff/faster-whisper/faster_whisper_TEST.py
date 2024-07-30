
from typing import List
# from whisper.utils import get_writer
from whisper_writer_copypaste import get_writer
import faster_whisper
import json
import os
import time
import torch
import langcodes


import urllib.parse
import urllib.request
import requests
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

filename = "100%252B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.opus"
audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/kaicenat/2143646862/100%252B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.opus"

filename = "Calculated-v5057810.opus"
audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.opus"


model_size = "large-v3"
model_size = "large-v2"
model_size = 'tiny'
model_size = "medium"

def downloadAudio():
    print(audio_url)
    response = requests.get(audio_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print("File downloaded successfully!")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def doWhisperFasterStuff(filename):
    print("Starting WhisperStuff!")
    # model_size = 'tiny'
    compute_type = "int8" # or float16
    cpu_threads = 4

    file_abspath = os.path.abspath(filename) # if relative_path =./assets/audio/ft.-v1964894986.opus then => file_abspath = C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\And_you_will_know_my_name_is_the_LORD-v40792901.opus
    file_name2 = os.path.basename(filename)   # And_you_will_know_my_name_is_the_LORD-v40792901.opus

    model = faster_whisper.WhisperModel(model_size, compute_type=compute_type,  cpu_threads=cpu_threads) # 4 default

    start_time = time.time()

    print("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    print("    file_abspath=" + file_abspath)
    print("    torch.cuda.is_available(): " + str(torch.cuda.is_available()))
    print("    model_size: " + model_size)

    #                                          language=lang_code
    segments, info = model.transcribe(file_abspath, language="en", condition_on_previous_text=False, vad_filter=True, beam_size=2, best_of=2) # vad_filter = something to prevents bugs. long loops being stuck
    

    print(f"Detected language {info.language} with probability {str(info.language_probability)}")

    result = {  "segments": [] }
    for segment in segments: # generator()
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}") 
        result["segments"].append({
            "start" : segment.start,
            "end" :   segment.end,
            "text" :  segment.text,
        })

    saved_caption_files = writeCaptionsLocally(result, file_name2)
    end_time = time.time() - start_time

    print("========================================")
    print("Complete!")
    print(f"Detected language {info.language} with probability {str(info.language_probability)}")
    print()
    print("run time =" + str(end_time))
    print()
    print("Saved files: " + str(saved_caption_files))
    print()
    print("model_size: " + model_size)
    print()
    print("========================================")

    return saved_caption_files

def writeCaptionsLocally(result, audio_basename):
    # FILE_EXTENSIONS_TO_SAVE = ["json", "vtt", "txt", "srt"]
    FILE_EXTENSIONS_TO_SAVE = ["json", "vtt", "txt"]
    saved_caption_files = []
    abs_path = os.path.abspath(audio_basename) 
    print("------   WRITE FILE   ------")
    print("abs_path: " + abs_path)
    print("audio_basename: " + audio_basename)
    filename_without_ext , file_extension = os.path.splitext(audio_basename) # [Calculated-v5057810, .mp3]

    for ext in FILE_EXTENSIONS_TO_SAVE:
        srt_writer = get_writer(ext, "./")
        srt_writer(result, audio_basename + ext)

        caption_file = filename_without_ext  + '.' + ext
        saved_caption_files.append(caption_file)
        print("Wrote - " + ext + " - " + caption_file)

    return saved_caption_files



if __name__ == "__main__":
    relative_path = downloadAudio()
    saved_caption_files = doWhisperFasterStuff(filename)
    print("GG!")
    print("GG!")
    exit(0)
#    mp3FastTranscribe(filename)
