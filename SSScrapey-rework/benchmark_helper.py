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

# $ python ./benchmark_helper.py -f "BarbaraWalters.mp3" -m "tiny" > tiny-barbara.txt 2>&1   &&
# $ python ./benchmark_helper.py -f "BarbaraWalters.mp3" -m "small" > small-barbara.txt 2>&1    &&
# $ python ./benchmark_helper.py -f "OPENASSISTANT+TAKES+ON+CHATGPT.mp3" -m "tiny" > tiny-chatgpt.txt 2>&1    &&
# $ python ./benchmark_helper.py -f "OPENASSISTANT+TAKES+ON+CHATGPT.mp3" -m "small" > small-chatgpt.txt 2>&1   

from pathlib import Path
import argparse
import controllers.MicroTranscriber.transcriber as transcriber
from models.Vod import Vod
import os 
import sys
import time
import torch


if __name__ == '__main__':
    ######################################################
    # DEFAULTS
    ######################################################
    # filename = "OPENASSISTANT+TAKES+ON+CHATGPT.mp3"
    # filename = "BarbaraWalters.mp3"
    filename = "./assets/audio/OPENASSISTANT+TAKES+ON+CHATGPT.mp3"
    filename = "./assets/audio/BarbaraWalters.mp3"
    
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
        relative_path = args.file
    print()
    print("sys.argv: " + str(sys.argv))
    print("args: " + str(args))
    print("args.file: " + str(args.file))
    vod = Vod(id="12345", channels_name_id="test_run")
    relative_path = "/assets/audio/test_audio_file.opus"
    print('yeah')
    saved_caption_files = transcriber.doWhisperStuff(vod, relative_path)