import os
import time

import urllib.parse
import urllib.request
import requests

import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available

import os
import time
import cloudwatch as Cloudwatch
import os
# import faster_whisper
# import faster_whisper.utils
# from whisper.utils import get_writer

# nvcc and cuda setup v2 https://www.freecodecamp.org/news/how-to-install-nvidia-cuda-toolkit-on-ubuntu/

# https://github.com/Vaibhavs10/insanely-fast-whisper/issues/158 vad = bad?

# filename = "Calculated-v5057810.opus"
# audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/5057810/Calculated-v5057810.opus"

# filename = "The_Geraniproject_I_Love_You_Guys-v28138895.opus"
# audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.us-east-1.amazonaws.com/channels/vod-audio/lolgeranimo/28138895/The_Geraniproject_I_Love_You_Guys-v28138895.opus"

# Challenger_Climb_Season_14_Begins_Adc_POV-v2028592547 ----> 250sec = 4.2 min
# Adc_Academy_-_How_to_Climb_on_Adc_in_Season_14_Birthday_Stream_im_so_old-v2036392694.opus ---->  456sec = 7.6 min
########################################################
# 
# apt-get install vim -y
# git pull
# pip install faster-whisper
# pip install flash-attn --no-build-isolation 
# pip install openai-whisper
#
########################################################
filename = "Challenger_Climb_Season_14_Begins_Adc_POV-v2028592547.opus"
audio_url = "https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/2028592547/Challenger_Climb_Season_14_Begins_Adc_POV-v2028592547.opus"

model_size_insane = "openai/whisper-medium"
model_size_insane = "openai/whisper-large-v3"
model_size_fast = "medium"
model_size_fast = "large-v3"
my_device = "cuda:0" if torch.cuda.is_available() else "cpu"

def logger():
    pass
# logger = Cloudwatch.log
logger = print


# "You are attempting to use Flash Attention 2.0 with a model not initialized on GPU. Make sure to move the model to GPU after initializing it on CPU with `model.to('cuda')`."
# ^ Ignore https://github.com/Vaibhavs10/insanely-fast-whisper/issues/141
def downloadAudio():
    logger(audio_url)
    response = requests.get(audio_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        logger("File downloaded successfully!")
    else:
        logger(f"Failed to download file. Status code: {response.status_code}")
# pipline tutorial https://huggingface.co/docs/transformers/v4.39.3/en/pipeline_tutorial
def goInsaneoMode():
    pipe = pipeline( # https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.pipeline
        "automatic-speech-recognition",
        model=model_size_insane, # select checkpoint from https://huggingface.co/openai/whisper-large-v3#model-details
#        model="openai/whisper-medium",
        torch_dtype=torch.float16,
        device=my_device,
        model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
    )
    
    if not is_flash_attn_2_available():
        pipe.model = pipe.model.to_bettertransformer()
    # if better_transformer:
    #     pipe.model = pipe.model.to_bettertransformer()

    # https://github.com/Vaibhavs10/insanely-fast-whisper/issues/6
    generate_kwargs = {
        # "beam_size": 5,
        "language": 'en',
        # "temperature": 0.2,
        "repetition_penalty": 1.25, # 1 = default = no penatlty
      #  "condition_on_previous_text": True,
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
    logger("Starting WhisperStuff!")
    logger(relative_path)
    file_abspath = os.path.abspath(relative_path) # if relative_path =./assets/audio/ft.-v1964894986.opus then => file_abspath = C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\And_you_will_know_my_name_is_the_LORD-v40792901.opus
    file_name = os.path.basename(relative_path) # And_you_will_know_my_name_is_the_LORD-v40792901.opus
    end_time = None

    logger("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    logger("    file_abspath=" + file_abspath)
    logger("    torch.cuda.is_available(): " + str(torch.cuda.is_available()))
    logger("    is_flash_attn_2_available(): " + str(is_flash_attn_2_available()))
    outputs, start_timeX = goInsaneoMode()
    logger("outputs")
    logger(outputs)
    audio_file_name = os.path.splitext(os.path.basename(filename))[0]
    srt_filename = f"{audio_file_name}.srt"
    with open(srt_filename, 'w') as srt_file:
        prev = 0
        for index, chunk in enumerate(outputs['chunks']):
            # logger('---')
            # logger(chunk['timestamp'][0])
            # logger(chunk['text'].strip())
            prev, start_time = seconds_to_srt_time_format(prev, chunk['timestamp'][0])
            prev, end_time = seconds_to_srt_time_format(prev, chunk['timestamp'][1])
#            //srt_file.write(f"{index + 1}\n")
            srt_file.write(f"{start_time} --> {end_time}: ")
            srt_file.write(f"{chunk['text'].strip()}\n")
            # logger(f"{index + 1}")
            # logger(f"{start_time} --> {end_time}")
            # logger(f"{chunk['text'].strip()}\n")
            logger(f"{start_time} --> {end_time}: ")
            logger(f"{chunk['text'].strip()}")
            # logger(f"{chunk['text'].strip()}\n")
        
        end_time = time.time() - start_timeX
        srt_file.write(f"Run time: {end_time}\n")
        srt_file.write(f"model_size_insane: {model_size_insane}\n")


    # saved_caption_files = writeCaptionsLocally(result, file_name)

    logger("========================================")
    logger("Complete!")
    # logger(f"Detected language {info.language} with probability {str(info.language_probability)}")
    # logger()
    logger("run time =" + str(end_time))
    # logger()
    # logger("Saved files: " + str(saved_caption_files))
    # logger()
    # logger("model_size: " + model_size)
    # logger()
    logger("========================================")
    time.sleep(300)
    return True


def seconds_to_srt_time_format(prev, seconds):
    if not (isinstance(seconds, int) or isinstance(seconds, float)):
        seconds = prev
    else:
        prev = seconds
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    return (prev, f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}")


# http://muzso.hu/2015/04/25/how-to-speed-up-slow-down-an-audio-stream-with-ffmpeg
# https://gist.github.com/frankrausch/f871b573060b4d0cf34a7d86077e433f
#
# $ ffmpeg -i .\BarbaraWaltersFAST.mp3 -filter:a "atempo=1.5" "BarbaWaltersFASTER.mp3"

# def mp3FastTranscribe(filename):
#     logger("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
#     logger("    torch.cuda.is_available(): " + str(torch.cuda.is_available()))
#     model = faster_whisper.WhisperModel(model_size_fast, compute_type="int8",  cpu_threads=16) # 4 default
#     # audio_path = "{}/{}/{}".format(main_dir, asset_dir, filename)

#     start_time = time.time()
#     segments, info = model.transcribe(filename, language="en")

#     result = {
#         "segments": []
#     }

#     for segment in segments:
#         logger("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
#         result["segments"].append({
#             "start" : segment.start,
#             "end" :   segment.end,
#             "text" :  segment.text,
#         })

#     end_time = time.time() - start_time
#     srt_writer = get_writer("srt", './')
#     srt_writer(result, filename + ".srt")

#     end_time = time.time() - start_time

#     logger("Detected language '%s' with probability %f" % (info.language, info.language_probability))
#     logger()
#     logger("run time =" + str(end_time))
#     logger()
#     logger("Completed: " + filename)





if __name__ == "__main__":
    relative_path = downloadAudio()
    saved_caption_files = doWhisperStuff(filename)
    time.sleep(120)
    logger("GG!")
    logger("GG!")
#    mp3FastTranscribe(filename)
