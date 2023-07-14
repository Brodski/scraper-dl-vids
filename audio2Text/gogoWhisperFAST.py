###########################################################################
#
# Faster Whisper transcription with CTranslate2
#
# https://github.com/guillaumekln/faster-whisper
# https://github.com/guillaumekln/faster-whisper
# https://github.com/guillaumekln/faster-whisper
##########################################################################
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

import env_app as env_varz

FILE_EXTENSIONS_TO_SAVE = ["json", "vtt"]

def main():
    ######################################################
    # DEFAULTS
    ######################################################
    # filename = "Bootcamp to Challenger - Gaming-v1767827635.f_Audio_Only.mp4"
    # filename = "Bootcamp to Challenger - Gaming-v1767827635.f_Audio_Only.mp3"
    # filename = "Bootcamp to Challenger ｜-v1747933567.f_Audio_Only-wtf.mp3"
    # filename = "Adc+Academy+-+Informative+Adc+Stream+-+GrandMaster+today？+[v1792628012].mp3"
    filename = "OPENASSISTANT+TAKES+ON+CHATGPT.mp3"
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
    print()
    print("sys.argv: " + str(sys.argv))
    print("args: " + str(args))
    print("args.file: " + str(args.file))

    run(model_size=model_size, filename=filename)


######################################################
# APP
######################################################
def run(*, model_size, lang_code=None, filename):
    model_size = env_varz.WHSP_MODEL_SIZE
    compute_type = env_varz.WHSP_COMPUTE_TYPE
    cpu_threads = int(env_varz.WHSP_CPU_THREADS)

    # model = faster_whisper.WhisperModel(model_size, device="cuda", compute_type="int8", cpu_threads=8) # 4 default 
    model = faster_whisper.WhisperModel(model_size, compute_type=compute_type,  cpu_threads=cpu_threads) # 4 default
    audio_abs_path = os.path.abspath(env_varz.A2T_ASSETS_AUDIO + '/' + filename)
    audio_basename = os.path.basename(env_varz.A2T_ASSETS_AUDIO + '/' + filename)

    start_time = time.time()

    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("audio_abs_path: " + audio_abs_path)
    print("torch.cuda.is_available(): " + str(torch.cuda.is_available()))
    # segments, info = model.transcribe(audio_abs_path, language="en")
    # segments, info = model.transcribe(audio_abs_path, language="en", condition_on_previous_text=False, vad_filter=True)
    segments, info = model.transcribe(audio_abs_path, language=lang_code, condition_on_previous_text=False, vad_filter=True, beam_size=2, best_of=2) # vad_filter = something to prevents bugs. long loops being stuck
    

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    print("model_size: " + model_size)

    result = { 
        "segments": []
    }

    for segment in segments: # generator()
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        result["segments"].append({
            "start" : segment.start,
            "end" :   segment.end,
            "text" :  segment.text,
        })


    saved_caption_files = writeCaptionsLocally(result, audio_basename)
    # removeAudio(audio_basename)
    print( "audio_basename: ")
    print(audio_basename)
    print(audio_basename)
    print(audio_basename)
    print(audio_basename)
    print(audio_basename)
    print(audio_basename)
    print(audio_basename)
    print(audio_basename)
    print(audio_basename)
    print(audio_basename)
    print(audio_basename)
    # HERE
    # HERE
    # HERE
    # HERE
    # HERE
    # HERE
    end_time = time.time() - start_time

    print("========================================")
    print("Complete!")
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    print()
    print("run time =" + str(end_time))
    print()
    print("Saved files: " + str(saved_caption_files))
    print()
    print("model_size: " + model_size)
    print()

    return saved_caption_files

def writeCaptionsLocally(result, audio_basename):
    print("------   WRITE FILE   ------")
    file_extensions = FILE_EXTENSIONS_TO_SAVE
    saved_caption_files = []
    for ext in file_extensions:
        srt_writer = get_writer(ext, env_varz.A2T_ASSETS_CAPTIONS)
        srt_writer(result, audio_basename + ext)
        print("audio_basename: " + audio_basename)
        print("audio_basename: " + audio_basename)
        print("audio_basename: " + audio_basename)
        print("audio_basename: " + audio_basename)

        filename, file_extension = os.path.splitext(audio_basename) # [Calculated-v5057810, .mp3]
        caption_file = filename + '.' + ext
        # pathy = os.path.join(env_varz.A2T_ASSETS_CAPTIONS, caption_base)
        # caption_file = os.path.basename(pathy)
        saved_caption_files.append(caption_file)
        print("Wrote - " + ext + " - " + caption_file)
    return saved_caption_files


if __name__ == '__main__':
    main()