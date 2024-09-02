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


# 
# ssh -p 40071 root@195.122.198.67 -L 8080:localhost:8080 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"
# ssh -p 40071 root@195.122.198.67 -L 8080:localhost:8080 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"
# ssh -p 40071 root@195.122.198.67 -L 8080:localhost:8080 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"
#
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

filename = "100%252B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.opus"
audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/kaicenat/2143646862/100%252B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.opus"

# model_size_insane = "openai/whisper-medium"
# model_size_insane = "openai/whisper-tiny"
model_size_insane = "openai/whisper-large-v3"
model_size_insane = "openai/whisper-large-v2"
model_size_insane = "openai/whisper-medium"
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
        
# pipline tutorial  https://huggingface.co/docs/transformers/v4.39.3/en/pipeline_tutorial
#                   https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.pipeline
def goInsaneoMode():
    pipe = pipeline( 
        "automatic-speech-recognition",
        model=model_size_insane, # select checkpoint from https://huggingface.co/openai/whisper-large-v3#model-details
        # torch_dtype=torch.float32, # LOCAL REQUIRES `torch.float32`
        torch_dtype=torch.float16, 
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
        return_timestamps=True,
        generate_kwargs = generate_kwargs
    )
    return outputs, start_time

def doInsaneWhisperStuffTest( relative_path: str):
    print("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("    xxxxxxx     doInsaneWhisperStuffTest()      xxxxxxx")
    print("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("    (doInsaneWhisperStuffTest) relative_path:",  relative_path)
    file_abspath = os.path.abspath(relative_path) # if relative_path =./assets/audio/ft.-v1964894986.opus then => file_abspath = C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\And_you_will_know_my_name_is_the_LORD-v40792901.opus
    file_name = os.path.basename(relative_path) # And_you_will_know_my_name_is_the_LORD-v40792901.opus
    end_time = None

    print("    (doInsaneWhisperStuffTest) file_abspath=" + file_abspath)
    print("    (doInsaneWhisperStuffTest) torch.cuda.is_available(): " + str(torch.cuda.is_available()))
    print("    (doInsaneWhisperStuffTest) is_flash_attn_2_available(): " + str(is_flash_attn_2_available()))
    outputs, start_timeX = goInsaneoMode()

    
    saved_caption_files = write_files(outputs, file_name)

    end_time = time.time() - start_timeX

    print("========================================")
    print("Complete!")
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


# http://muzso.hu/2015/04/25/how-to-speed-up-slow-down-an-audio-stream-with-ffmpeg
# https://gist.github.com/frankrausch/f871b573060b4d0cf34a7d86077e433f
#
# $ ffmpeg -i .\BarbaraWaltersFAST.mp3 -filter:a "atempo=1.5" "BarbaWaltersFASTER.mp3"





if __name__ == "__main__":
    relative_path = downloadAudio()
    saved_caption_files = doInsaneWhisperStuffTest(filename)
    print("GG!")
    print("GG!")
    exit(0)
#    mp3FastTranscribe(filename)
