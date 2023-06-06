# python -m venv venvA2T
# python -m pip install faster-whisper
# python -m pip install openai-whisper

# $ python ./gogoWhisperFAST.py -f "BarbaraWalters.mp3" -m "tiny" > tiny-barbara.txt 2>&1   &&
# $ python ./gogoWhisperFAST.py -f "BarbaraWalters.mp3" -m "small" > small-barbara.txt 2>&1    &&
# $ python ./gogoWhisperFAST.py -f "OPENASSISTANT+TAKES+ON+CHATGPT.mp3" -m "tiny" > tiny-chatgpt.txt 2>&1    &&
# $ python ./gogoWhisperFAST.py -f "OPENASSISTANT+TAKES+ON+CHATGPT.mp3" -m "small" > small-chatgpt.txt 2>&1   

import faster_whisper
# import whisper.utils
from whisper.utils import get_writer

import os 
import time
import torch
import sys
import argparse
from pathlib import Path

# Should be env vairable for local or micro
ASSET_DIR_RELATIVE = "./assets/audio/"
OUTPUT_DIR_RELATIVE = "./assets/output"
MAIN_DIR = r'/home/ssm-user/scraper-dl-vids'
MAIN_DIR = r'C:/Users/BrodskiTheGreat/Desktop/desktop/Code/scraper-dl-vids'

def main():
    ######################################################
    # DEFAULTS
    ######################################################
    # filename = "Bootcamp to Challenger - Gaming-v1767827635.f_Audio_Only.mp4"
    # filename = "Bootcamp to Challenger - Gaming-v1767827635.f_Audio_Only.mp3"
    # filename = "Bootcamp to Challenger ｜-v1747933567.f_Audio_Only-wtf.mp3"
    filename = "OPENASSISTANT+TAKES+ON+CHATGPT.mp3"
    # filename = "Adc+Academy+-+Informative+Adc+Stream+-+GrandMaster+today？+[v1792628012].mp3"
    filename = "BarbaraWalters.mp3"
    
    #model_size = "large-v2"
    #model_size = "medium"
    #model_size = "small"
    model_size = "tiny"

    ######################################################
    #  COMMAND LINE ARGS
    ######################################################
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', "--file", help="file to use")
    parser.add_argument('-m', "--model", help="model: tiny, base, small, med, large-v2, tiny.en, base.en, ... https://github.com/openai/whisper#available-models-and-languages  ||  https://huggingface.co/openai/whisper-large")
    args = parser.parse_args()

    if args.model:
        model_size = args.model
    if args.file:
        filename = args.file
        # filename = Path(args.file)
        
    print ("sys.argv")
    print (sys.argv)
    print ("args")
    print ("args")
    print ("args")
    print (args)
    print ("args.file")
    print (args.file)
    print (args.file)

    run(model_size=model_size, filename=filename)


######################################################
# APP
######################################################
def run(*, model_size, filename):
    # model = WhisperModel(model_size, device="cuda", compute_type="float16")
    # model = faster_whisper.WhisperModel(model_size, compute_type="int8")
    # model = faster_whisper.WhisperModel(model_size, device="cuda", compute_type="int8",  cpu_threads=8) # 4 default
    # model = faster_whisper.WhisperModel(model_size, device="cuda", compute_type="int8", cpu_threads=8) # 4 default
    model = faster_whisper.WhisperModel(model_size, compute_type="int8",  cpu_threads=16) # 4 default
    audio_path = "{}/{}/{}".format(MAIN_DIR, ASSET_DIR_RELATIVE, filename)
    audio_abs_path = os.path.abspath(ASSET_DIR_RELATIVE + '/' + filename)
    audio_basename = os.path.basename(ASSET_DIR_RELATIVE + '/' + filename)

    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print(audio_path)
    print(audio_path)
    print(audio_abs_path)
    print(audio_abs_path)
    # exit()
    start_time = time.time()

    print("torch.cuda.is_available(): " + str(torch.cuda.is_available()))
    print("start!")
    # segments, info = model.transcribe(audio_abs_path, language="en", condition_on_previous_text=False, beam_size=2, best_of=2)
    # segments, info = model.transcribe(audio_abs_path, language="en", condition_on_previous_text=False, vad_filter=True)
    # segments, info = model.transcribe(audio_abs_path, language="en")
    segments, info = model.transcribe(audio_abs_path, language="en", condition_on_previous_text=False, vad_filter=True, beam_size=2, best_of=2)

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
    file_extension = "json"
    srt_writer = get_writer(file_extension, OUTPUT_DIR_RELATIVE)
    srt_writer(result, audio_basename + file_extension)


    print("========================================")
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    print()
    print("run time =" + str(end_time))
    print()
    print("Completed srt: " +  audio_basename + ".srt")
    print("Completed: " + audio_path)

if __name__ == '__main__':
    main()