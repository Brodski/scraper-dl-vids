
from typing import List
import faster_whisper
import json
import os
import time
import torch
import langcodes

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def doWhisperStuff():
    print("Starting WhisperStuff!")

    PATH_LONG = r"C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\src\controllers\MicroSentimentz" + "\\"
    file_name = "outfile10k.opus"
    model_size = "distil-small.en"
    compute_type = "int8"
    cpu_threads = 8

    file_abspath = os.path.abspath(PATH_LONG + file_name) # if relative_path =./assets/audio/ft.-v1964894986.opus then => file_abspath = C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\And_you_will_know_my_name_is_the_LORD-v40792901.opus


    model = faster_whisper.WhisperModel(model_size, compute_type=compute_type,  cpu_threads=cpu_threads) # 4 default

    start_time = time.time()
    print("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("    file_abspath=" + file_abspath)
    print("    torch.cuda.is_available(): " + str(torch.cuda.is_available()))
    print("    model_size: " + model_size)

    segments, info = model.transcribe(file_abspath, condition_on_previous_text=False, vad_filter=True, beam_size=2, best_of=2) # vad_filter = something to prevents bugs. long loops being stuck

    print(f"Detected language {info.language} with probability {str(info.language_probability)}")

    result = {  "segments": [] }

    for segment in segments: # generator()
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}") 
        result["segments"].append({
            "start" : segment.start,
            "end" :   segment.end,
            "text" :  segment.text,
        })

    end_time = time.time() - start_time

    print("========================================")
    print("Complete!")
    print(f"Detected language {info.language} with probability {str(info.language_probability)}")
    print()
    print("run time =" + str(end_time))
    print()
    print("model_size: " + model_size)
    print()
    print("========================================")

    return result

def shitJson(result):
    print(result)
    for seg in result["segments"]:
        # print(seg)
        print("{")
        print(f'  "start": "{seg["start"]}",')
        print(f'  "end": "{seg["end"]}",')
        print(f'''  "text": "{seg["text"].replace('"',"'") }"''')
        print("},")

if __name__ == "__main__":
    result = doWhisperStuff()
    shitJson(result)
