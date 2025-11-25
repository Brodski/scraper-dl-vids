
from controllers.MicroTranscriber.cloudwatch import Cloudwatch 
from models.Vod import Vod
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available
import torch
import langcodes
import datetime
# from controllers.MicroTranscriber.Writer import Writer
import json
import os
# import env_file as env_varz
from env_file import env_varz
import logging
from utils.logging_config import LoggerConfig

# logger = Cloudwatch.log
def logger():
    pass
logger: logging.Logger = LoggerConfig("micro", env_varz.WHSP_IS_CLOUDWATCH == "True").get_logger()

def doInsaneWhisperStuff(vod: Vod, relative_path: str, isDebug=False):
    print("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("    xxxxxxx     doInsaneWhisperStuff()      xxxxxxx")
    print("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    def get_language_code(full_language_name):
        try:
            language_code = langcodes.find(full_language_name).language
            return language_code
        except:
            return None
    lang_code = get_language_code(vod.language)
    model_size_insane = env_varz.WHSP_MODEL_SIZE # "openai/whisper-tiny"
    compute_type = env_varz.WHSP_COMPUTE_TYPE
    cpu_threads = int(env_varz.WHSP_CPU_THREADS)

    my_device = "cuda:0" if torch.cuda.is_available() else "cpu"

    file_abspath = os.path.abspath(relative_path) # if relative_path =./assets/audio/ft.-v1964894986.opus then => file_abspath = C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\And_you_will_know_my_name_is_the_LORD-v40792901.opus
    file_name = os.path.basename(relative_path) # And_you_will_know_my_name_is_the_LORD-v40792901.opus
    start_time = time.time()

    logger("    (doInsaneWhisperStuff) Channel=" + vod.channels_name_id)
    logger("    (doInsaneWhisperStuff) model_size_insane: " + model_size_insane)
    logger("    (doInsaneWhisperStuff) torch.cuda.is_available(): " + str(torch.cuda.is_available()))
    logger("    (doInsaneWhisperStuff) is_flash_attn_2_available(): " + str(is_flash_attn_2_available()))
    logger("    (doInsaneWhisperStuff) Running it ...")


    pipe = pipeline( # https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.pipeline
        "automatic-speech-recognition",
        model=model_size_insane, 
        torch_dtype=torch.float16,
        device=my_device,
        model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
    )
    # https://github.com/Vaibhavs10/insanely-fast-whisper/issues/6
    generate_kwargs = {
        "language": lang_code,
        # "temperature": 0.2,
        "repetition_penalty": 1.25, # 1 = default = no penatlty
        "task": "transcribe",
    }

    if isDebug and False:
        outputs =  {'text': " Let's see, this is PTR. Crazy ketchup come! Alright maybe clang because I want to be part of the cake again I'm glad we're you can do it. Imagine that smoking, Kelly? It's more like needles! Not really against smoking anything Got someone out...I know it didn't heal you. You're on me hard! I got my wallet These alley i'm blinding Oh wow don' even hit him The files bug Yeah are ya been healing with me? No The foul's bug. Yeah, you been helping me? Why are What're your doing what do we You Where aren't Are What are you doing? what're ya doin'? Why aren't y'all u goin'! You mean, you second shit?! It's a good one, I i gonna do this by myself? l don't even need your help. Don t leave me here to help! Let him take care of you and then he just got absolutely brilliant Just fucking kill be one of them! Oh my god... What's up, a fowler? WHAT'S UP?! Aaaaaahhhhhh", 'chunks': [{'timestamp': (0.0, 7.0), 'text': " Let's see, this is PTR."}, {'timestamp': (7.02, 8.5), 'text': ' Crazy ketchup come!'}, {'timestamp': (8.52, 11.52), 'text': ' Alright maybe clang because I want to be part of the cake again'}, {'timestamp': (11.54, 13.67), 'text': " I'm glad we're you can do it."}, {'timestamp': (14.67, 15.67), 'text': ' Imagine that smoking, Kelly?'}, {'timestamp': (17.67, 23.67), 'text': " It's more like needles! Not really against smoking anything"}, {'timestamp': (25.13, 25.63), 'text': " Got someone out...I know it didn't heal you."}, {'timestamp': (26.43, 26.53), 'text': " You're on me hard!"}, {'timestamp': (27.33, 28.93), 'text': ' I got my wallet'}, {'timestamp': (30.03, 30.63), 'text': " These alley i'm blinding"}, {'timestamp': (31.63, 32.33), 'text': " Oh wow don' even hit him"}, {'timestamp': (33.13, 34.76), 'text': " The files bug Yeah are ya been healing with me? No The foul's bug."}, {'timestamp': (36.76, 37.26), 'text': ' Yeah, you been helping me?'}, {'timestamp': (38.46, 38.56), 'text': ' Why are'}, {'timestamp': (40.56, 40.58), 'text': " What're your doing"}, {'timestamp': (41.52, 42.16), 'text': ' what do we'}, {'timestamp': (43.44, 43.84), 'text': ' You'}, {'timestamp': (45.2, 46.07), 'text': " Where aren't Are What are you doing? what're ya doin'?"}, {'timestamp': (47.17, 48.37), 'text': " Why aren't y'all u goin'!"}, {'timestamp': (50.07, 54.87), 'text': ' You mean, you second shit?!'}, {'timestamp': (58.33, 58.35), 'text': " It's a good one, I i gonna do this by myself?"}, {'timestamp': (60.33, 60.35), 'text': " l don't even need your help."}, {'timestamp': (62.35, 62.37), 'text': ' Don t leave me here to help!'}, {'timestamp': (66.33, 66.35), 'text': ' Let him take care of you and then he just got absolutely brilliant'}, {'timestamp': (69.52, 71.02), 'text': ' Just fucking kill be one of them!'}, {'timestamp': (72.02, 72.04), 'text': ' Oh my god...'}, {'timestamp': (74.02, 74.04), 'text': " What's up, a fowler?"}, {'timestamp': (75.04, 76.04), 'text': " WHAT'S UP?!"}, {'timestamp': (77.04, None), 'text': ' Aaaaaahhhhhh'}]}
    else:
        outputs = pipe(
            file_abspath,
            chunk_length_s=16, # 16 works pretty good # stide = chunk / 6
            batch_size=24,
            # return_timestamps="word",
            return_timestamps=True,
            generate_kwargs = generate_kwargs
        )
    
    logger.debug("outputs length:" + str(len(outputs)))
    # logger(outputs)
    logger()
    logger()

    saved_caption_files = write_files(outputs, file_name)

    end_time = time.time() - start_time

    logger("========================================")
    logger("Complete!")
    logger(f"Detected language {lang_code}!")
    logger()
    logger("run time =" + str(end_time))
    logger()
    logger("Saved files: " + str(saved_caption_files))
    logger()
    logger("model_size_insane: " + model_size_insane)
    logger()
    logger("========================================")
    return saved_caption_files

def write_files(outputs, filename):
    FILE_EXTENSIONS_TO_SAVE = ["json", "vtt", "txt", "srt"]
    saved_caption_files = []
    filename_without_ext , file_extension = os.path.splitext(filename) # [Calculated-v5057810, .mp3]

    for ext in FILE_EXTENSIONS_TO_SAVE:
        writer: Writer = Writer(ext)
        writer.write(outputs, filename, env_varz.WHSP_A2T_ASSETS_CAPTIONS)
        saved_caption_files.append(f"{filename_without_ext}.{ext}")

    return saved_caption_files






class Writer:
    extension: str
    debug_print: bool

    def __init__(self, extension):
        self.extension = extension
        self.debug_print = True
        self.debug_count = 0

    def write(self, outputs, filename, directory_save):
        print(self.extension)
        print(self.extension)
        print(self.extension)
        audio_file_name = os.path.splitext(os.path.basename(filename))[0]
        subtitle_filename = f"{audio_file_name}.{self.extension}"

        json_transcript = { "segments" : [] }
        with open(directory_save + subtitle_filename, 'w') as subbed_file:
            if self.extension == "txt":
                subbed_file.write(outputs["text"].strip())
                return
            if self.extension == "vtt":
                self.write_print(subbed_file, "WEBVTT\n\n")

            prev = 0
            for index, chunk in enumerate(outputs['chunks']):
                prev, start_time = self.seconds_to_thee_time_format(prev, chunk['timestamp'][0])
                prev, end_time = self.seconds_to_thee_time_format(prev, chunk['timestamp'][1])

                if self.debug_print and self.debug_count < 20:
                    print(f"{start_time} --> {end_time}\n", end="")
                    print(f"{chunk['text'].strip()}\n\n", end="")
                    self.debug_count += 1
                    if self.debug_count == 20:
                        print("Transcripts no longer printing, view s3 for more ...")

                if self.extension == "srt":
                    subbed_file.write(f"{index + 1}\n")
                    subbed_file.write(f"{start_time} --> {end_time}\n")
                    subbed_file.write(f"{chunk['text'].strip()}\n\n")
                if self.extension == "vtt":
                    subbed_file.write(f"{start_time} --> {end_time}\n")
                    subbed_file.write(f"{chunk['text'].strip()}\n\n")
                if self.extension == "json":
                    json_transcript["segments"].append( {
                        "start": float(start_time),
                        "end": float(end_time),
                        "text": chunk['text'].strip()
                    })
                # if self.extension == "tsv":
                #     pass
            
            if self.extension == "json":
                print("WE DOING THE JSON")
                json.dump(json_transcript, subbed_file)
                print("DUMPED!")

    def write_print(self, file, txt):
        file.write(txt)
        print(txt, end="")

    def seconds_to_thee_time_format(self, prev, seconds):
        if not (isinstance(seconds, int) or isinstance(seconds, float)):
            seconds = prev
        else:
            prev = seconds
        sec_OG = seconds
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)

        prev_next = None
        if self.extension == "srt":
            prev_next = (prev, f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}")
        if self.extension == "vtt":
            if hours > 0:
                prev_next = (prev, f"{hours:02d}:{minutes:02d}:{int(seconds):02d}.{milliseconds:03d}")
            else:
                prev_next = (prev, f"{minutes:02d}:{int(seconds):02d}.{milliseconds:03d}")
        if self.extension == "json":
            # prev_next = (prev, f"{int(seconds)}.{milliseconds:03d}")
            prev_next = (prev, f"{int(sec_OG)}.{milliseconds:03d}")
            return (prev, sec_OG)
        return prev_next



    
