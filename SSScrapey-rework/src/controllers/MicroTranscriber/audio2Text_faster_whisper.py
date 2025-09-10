from models.Vod import Vod
from typing import List
# from whisper.utils import get_writer
from controllers.MicroTranscriber.whisper_writer_copypaste import get_writer
import env_file as env_varz
import faster_whisper
import json
import os
import time
import torch
import langcodes
from controllers.MicroTranscriber.cloudwatch import Cloudwatch
import logging
from utils.logging_config import LoggerConfig
from datetime import datetime

# logger = Cloudwatch.log
def logger():
    pass
logger: logging.Logger = LoggerConfig("micro", env_varz.WHSP_IS_CLOUDWATCH == "True").get_logger()



class Audio2Text:
    count_logger = 0

    current_num = None
    download_batch_size = None
    model = None
    completed_uploaded_tscripts = []

    @classmethod
    def doWhisperStuff(cls, vod: Vod, relative_path: str):
        logger.debug("Starting WhisperStuff!")
        def get_language_code(full_language_name):
            try:
                language_code = langcodes.find(full_language_name).language
                return language_code
            except Exception as e:
                logger.debug(f"Error finding language code: {str(e)}")
                return None

        lang_code = get_language_code(vod.language)
        model_size = env_varz.WHSP_MODEL_SIZE
        compute_type = env_varz.WHSP_COMPUTE_TYPE
        cpu_threads = int(env_varz.WHSP_CPU_THREADS)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if env_varz.ENV == "local" and device == "cuda":
            compute_type = "float16"
        file_abspath = os.path.abspath(relative_path) # if relative_path =./assets/audio/ft.-v1964894986.opus then => file_abspath = C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\SSScrapey-rework\And_you_will_know_my_name_is_the_LORD-v40792901.opus
        file_name = os.path.basename(relative_path) # And_you_will_know_my_name_is_the_LORD-v40792901.opus

        logger.debug("loading model........")
        if cls.model is None:
            cls.model = faster_whisper.WhisperModel(model_size, device=device, compute_type=compute_type,  cpu_threads=cpu_threads) # 4 default

        logger.debug("    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        logger.debug("    Channel=" + vod.channels_name_id)
        logger.debug("    file_abspath=" + file_abspath)
        logger.debug("    torch.cuda.is_available(): " + str(torch.cuda.is_available()))
        logger.debug("    model_size: " + model_size)

        if env_varz.ENV == "local":
            import ctypes
            ctypes.CDLL("C:/Program Files/NVIDIA/CUDNN/v9.13/bin/13.0/cudnn_ops_infer64_8.dll")

        start_time_model = time.time()

        segments, info = cls.model.transcribe(file_abspath, language=lang_code, condition_on_previous_text=False, vad_filter=True, beam_size=2, best_of=2) # vad_filter = something to prevents bugs. long loops being stuck

        end_time_model = time.time() - start_time_model
        start_time_vod = time.time()


        result = {  "segments": [] }
        cls.count_logger = 0
        for segment in segments: # generator()
            # logger.debug(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}") 
            cls.aux_logger(segment, vod)
            result["segments"].append({
                "start" : segment.start,
                "end" :   segment.end,
                "text" :  segment.text,
            })

        saved_caption_files = cls.writeCaptionsLocally(result, file_name)
        end_time_vod = time.time() - start_time_vod

        logger.debug("========================================")
        logger.debug("Complete!")
        logger.debug("model_size: " + model_size)
        logger.debug(f"Detected language {info.language} with probability {str(info.language_probability)}")
        logger.debug("")
        logger.debug(f"Channel: {vod.channels_name_id}")
        logger.debug(f"{vod.id}: {vod.title}")
        logger.debug("")
        logger.debug("Model load run time =" + str(end_time_model))
        logger.debug("Vod transcribe run time =" + str(end_time_vod))
        logger.debug("Model + Vod =" + str(end_time_model + end_time_vod))
        # logger.debug("")
        # logger.debug("Saved files: " + str(saved_caption_files))
        logger.debug("")
        logger.debug("========================================")

        return saved_caption_files

    @classmethod
    def writeCaptionsLocally(self, result, audio_basename):
        # FILE_EXTENSIONS_TO_SAVE = ["json", "vtt", "txt", "srt"]
        FILE_EXTENSIONS_TO_SAVE = ["json", "vtt", "txt"]
        saved_caption_files = []
        abs_path = os.path.abspath(audio_basename) 
        logger.debug("------   WRITE FILE   ------")
        filename_without_ext , file_extension = os.path.splitext(audio_basename) # [Calculated-v5057810, .mp3]

        for ext in FILE_EXTENSIONS_TO_SAVE:
            srt_writer = get_writer(ext, env_varz.WHSP_A2T_ASSETS_CAPTIONS)
            srt_writer(result, audio_basename + ext)

            caption_file = filename_without_ext  + '.' + ext
            saved_caption_files.append(caption_file)
            logger.debug(ext + ": " + caption_file)

        return saved_caption_files

    @classmethod
    def aux_logger(cls, segment, vod: Vod):
        cls.count_logger = cls.count_logger + 1
        if cls.count_logger % 200 == 0 and not env_varz.ENV == "local":
            logger.debug("... still transcribing" + str(cls.count_logger))
        elif env_varz.ENV == "local":
            # logger.debug(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
            current_time = datetime.now().strftime("%H:%M:%S")
            
            msg = f"{cls.current_num} of {cls.download_batch_size}|id:{vod.id}"
            print(f"{current_time}|{msg}|[{segment.start:.0f}s -> {segment.end:.0f}s] {segment.text}")

            
            
