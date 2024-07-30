from models.Vod import Vod
from typing import List
from whisper.utils import get_writer
import env_file as env_varz
import faster_whisper
import json
import os
import time
import torch
import langcodes
from controllers.MicroTranscriber.cloudwatch import Cloudwatch 

def logger():
    pass
logger = Cloudwatch.log

class Audio2Text:
    @classmethod
    def doWhisperStuff(cls, vod: Vod, relative_path: str):
        logger("Starting WhisperStuff!")
        def get_language_code(full_language_name):
            try:
                language_code = langcodes.find(full_language_name).language
                return language_code
            except Exception as e:
                logger(f"Error finding language code: {str(e)}")
                return None
        lang_code = get_language_code(vod.language)
        model_size = (env_varz.WHSP_MODEL_SIZE + ".en") if lang_code == "en" else env_varz.WHSP_MODEL_SIZE
        compute_type = env_varz.WHSP_COMPUTE_TYPE
        cpu_threads = int(env_varz.WHSP_CPU_THREADS)

        file_abspath = os.path.abspath(relative_path) # if relative_path =./assets/audio/ft.-v1964894986.opus then => file_abspath = C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\And_you_will_know_my_name_is_the_LORD-v40792901.opus
        file_name = os.path.basename(relative_path) # And_you_will_know_my_name_is_the_LORD-v40792901.opus

        # model = faster_whisper.WhisperModel(model_size, device="cuda", compute_type="int8", cpu_threads=8)
        model = faster_whisper.WhisperModel(model_size, compute_type=compute_type,  cpu_threads=cpu_threads) # 4 default

        start_time = time.time()

        logger("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        logger("    Channel=" + vod.channels_name_id)
        logger("    file_abspath=" + file_abspath)
        logger("    torch.cuda.is_available(): " + str(torch.cuda.is_available()))
        logger("    model_size: " + model_size)

        # segments, info = model.transcribe(audio_abs_path, language="en")
        # segments, info = model.transcribe(audio_abs_path, language="en", condition_on_previous_text=False, vad_filter=True)
        segments, info = model.transcribe(file_abspath, language=lang_code, condition_on_previous_text=False, vad_filter=True, beam_size=2, best_of=2) # vad_filter = something to prevents bugs. long loops being stuck
        

        logger(f"Detected language {info.language} with probability {str(info.language_probability)}")

        result = {  "segments": [] }
        for segment in segments: # generator()
            logger(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}") 
            result["segments"].append({
                "start" : segment.start,
                "end" :   segment.end,
                "text" :  segment.text,
            })

        saved_caption_files = cls.writeCaptionsLocally(result, file_name)
        end_time = time.time() - start_time

        logger("========================================")
        logger("Complete!")
        logger(f"Detected language {info.language} with probability {str(info.language_probability)}")
        logger()
        logger("run time =" + str(end_time))
        logger()
        logger("Saved files: " + str(saved_caption_files))
        logger()
        logger("model_size: " + model_size)
        logger()
        logger("========================================")

        return saved_caption_files

    @classmethod
    def writeCaptionsLocally(self, result, audio_basename):
        # FILE_EXTENSIONS_TO_SAVE = ["json", "vtt", "txt", "srt"]
        FILE_EXTENSIONS_TO_SAVE = ["json", "vtt", "txt"]
        saved_caption_files = []
        abs_path = os.path.abspath(audio_basename) 
        logger("------   WRITE FILE   ------")
        logger("abs_path: " + abs_path)
        logger("audio_basename: " + audio_basename)
        filename_without_ext , file_extension = os.path.splitext(audio_basename) # [Calculated-v5057810, .mp3]

        for ext in FILE_EXTENSIONS_TO_SAVE:
            srt_writer = get_writer(ext, env_varz.WHSP_A2T_ASSETS_CAPTIONS)
            srt_writer(result, audio_basename + ext)

            caption_file = filename_without_ext  + '.' + ext
            saved_caption_files.append(caption_file)
            logger("Wrote - " + ext + " - " + caption_file)

        return saved_caption_files

