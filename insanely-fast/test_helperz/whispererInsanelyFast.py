import os
import time

import urllib.parse
import urllib.request
import requests

import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available
from Writer import Writer

# insanely-fast-whisper --model openai/whisper-base --device cuda:0 --dtype float32 --batch-size 8 --better-transformer --chunk-length 30 your_audio_file.wav
# insanely-fast-whisper --model openai/whisper-base --device cuda:0 --dtype float32 --batch-size 8 --better-transformer --chunk-length 30 --file-name  ..\SSScrapey-rework\assets\audio\Climbing_to_GrandMaster_on_Main_Adc_Academy_later-v2040455208.opus
# insanely-fast-whisper --model openai/whisper-base --file-name  ..\SSScrapey-rework\assets\audio\Climbing_to_GrandMaster_on_Main_Adc_Academy_later-v2040455208.opus
# 
# cd Desktop\desktop\Code\scraper-dl-vids\insanely-fast\zluda
# .\zluda.exe -- C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\insanely-fast\venv\Scripts\insanely-fast-whisper.exe --model openai/whisper-base --file-name  ..\..\SSScrapey-rework\assets\audio\Climbing_to_GrandMaster_on_Main_Adc_Academy_later-v2040455208.opus

########################################################
# 
# apt-get install vim -y
# git pull
# pip install faster-whisper
# pip install flash-attn --no-build-isolation 
# pip install openai-whisper
#

# import faster_whisper
# import faster_whisper.utils
# from whisper.utils import get_writer

# nvcc and cuda setup v2 https://www.freecodecamp.org/news/how-to-install-nvidia-cuda-toolkit-on-ubuntu/

# https://github.com/Vaibhavs10/insanely-fast-whisper/issues/158 vad = bad?
#
#
########################################################

filename = "Calculated-v5057810.opus"
audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.opus"

filename = "Challenger_Climb_Season_14_Begins_Adc_POV-v2028592547.opus"
audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/2028592547/Challenger_Climb_Season_14_Begins_Adc_POV-v2028592547.opus"

filename = "The_Geraniproject_I_Love_You_Guys-v28138895.opus"
audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.us-east-1.amazonaws.com/channels/vod-audio/lolgeranimo/28138895/The_Geraniproject_I_Love_You_Guys-v28138895.opus"

# filename = "Calculated-v5057810.opus"
# audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.opus"

filename = "GUSTABO_GARCIA_-_SpainRp_dia_18-v2060795159.opus"
audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/auronplay/2060795159/GUSTABO_GARCIA_-_SpainRp_dia_18-v2060795159.opus"

# model_size_insane = "openai/whisper-medium"
# model_size_insane = "openai/whisper-tiny"
model_size_insane = "openai/whisper-large-v3"
model_size_fast = "medium"
model_size_fast = "large-v3"
my_device = "cuda:0" if torch.cuda.is_available() else "cpu"


# "You are attempting to use Flash Attention 2.0 with a model not initialized on GPU. Make sure to move the model to GPU after initializing it on CPU with `model.to('cuda')`."
# ^ Ignore https://github.com/Vaibhavs10/insanely-fast-whisper/issues/141
def downloadAudio():
    print(audio_url)
    response = requests.get(audio_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print("File downloaded successfully!")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        
# pipline tutorial https://huggingface.co/docs/transformers/v4.39.3/en/pipeline_tutorial
def goInsaneoMode():
    pipe = pipeline( # https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.pipeline
        "automatic-speech-recognition",
        model=model_size_insane, # select checkpoint from https://huggingface.co/openai/whisper-large-v3#model-details
        torch_dtype=torch.float16, # LOCAL REQUIRES `torch.float32`
        device=my_device,
        model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
    )
    
    # https://github.com/Vaibhavs10/insanely-fast-whisper/issues/6
    generate_kwargs = {
        "language": 'en',
        "repetition_penalty": 1.25, # 1 = default = no penatlty
        "task": "transcribe",
    }
    start_time = time.time()
    outputs = pipe(
        filename,
        chunk_length_s=16, # 16 works pretty good # stide = chunk / 6
        batch_size=24,
        # return_timestamps="word",
        return_timestamps=True,
        generate_kwargs = generate_kwargs
    )
    return outputs, start_time

def doWhisperStuff( relative_path: str):
    print("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("    xxxxxxx     doWhisperStuff()      xxxxxxx")
    print("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("    (doWhisperStuff) relative_path:",  relative_path)
    file_abspath = os.path.abspath(relative_path) # if relative_path =./assets/audio/ft.-v1964894986.opus then => file_abspath = C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\And_you_will_know_my_name_is_the_LORD-v40792901.opus
    file_name = os.path.basename(relative_path) # And_you_will_know_my_name_is_the_LORD-v40792901.opus
    end_time = None

    print("    (doWhisperStuff) file_abspath=" + file_abspath)
    print("    (doWhisperStuff) torch.cuda.is_available(): " + str(torch.cuda.is_available()))
    print("    (doWhisperStuff) is_flash_attn_2_available(): " + str(is_flash_attn_2_available()))
    outputs, start_timeX = goInsaneoMode()

    
    # saved_caption_files = writeCaptionsLocally(result, file_name)
    saved_caption_files = write_files(outputs, file_name)

    end_time = time.time() - start_timeX

    print("========================================")
    print("Complete!")
    # print(f"Detected language {info.language} with probability {str(info.language_probability)}")
    # print()
    print("run time =" + str(end_time))
    print()
    print("Saved files: " + str(file_name))
    print()
    print("model_size_insane: " + model_size_insane)
    print()
    print("========================================")
    return True


def write_files(outputs, filename):
    FILE_EXTENSIONS_TO_SAVE = ["json", "vtt", "txt", "srt"]
    saved_caption_files = []
    filename_without_ext , file_extension = os.path.splitext(filename) # [Calculated-v5057810, .mp3]

    for ext in FILE_EXTENSIONS_TO_SAVE:
        writer: Writer = Writer(ext)
        writer.write(outputs, filename, "./")
        saved_caption_files.append(f"{filename_without_ext}.{ext}")

    return saved_caption_files


# def seconds_to_srt_time_format(prev, seconds):
#     if not (isinstance(seconds, int) or isinstance(seconds, float)):
#         seconds = prev
#     else:
#         prev = seconds
#     hours = seconds // 3600
#     seconds %= 3600
#     minutes = seconds // 60
#     seconds %= 60
#     milliseconds = int((seconds - int(seconds)) * 1000)
#     hours = int(hours)
#     minutes = int(minutes)
#     seconds = int(seconds)
#     return (prev, f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}")


# http://muzso.hu/2015/04/25/how-to-speed-up-slow-down-an-audio-stream-with-ffmpeg
# https://gist.github.com/frankrausch/f871b573060b4d0cf34a7d86077e433f
#
# $ ffmpeg -i .\BarbaraWaltersFAST.mp3 -filter:a "atempo=1.5" "BarbaWaltersFASTER.mp3"





if __name__ == "__main__":
    relative_path = downloadAudio()
    saved_caption_files = doWhisperStuff(filename)
    print("GG!")
    print("GG!")
    exit(0)
#    mp3FastTranscribe(filename)
