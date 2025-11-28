import re
import subprocess
import logging
import traceback
from typing import List
from models.Vod import Vod
from utils.logging_config import LoggerConfig
from controllers.MicroTranscriber.utils import TOO_BIG_LENGTH
# import env_file as env_varz
from env_file import env_varz
from models.Silence import Silence
from models.Splitted import Splitted
import bisect


def logger():
    pass
logger: logging.Logger = LoggerConfig("micro", env_varz.WHSP_IS_CLOUDWATCH == "True").get_logger()


# NOISE
#  ffmpeg -i input.opus -af silencedetect=noise=-30dB:d=10 -f null -

# SPLIT
# ffmpeg -i input_file -ss 106200 -to 145500 -c copy output_file

SPLIT_LENGTH = 57600 # 16 hours
TOO_BIG_LENGTH_X = TOO_BIG_LENGTH # IMPORTED # 18 hours


def splitHugeFile(vod: Vod, relative_path: str) -> List[Splitted]:
    noise_vol    = "30dB"
    duration     = "10" # seconds

    # My code is bugged and shit, i'll need to fix it another day
    split = Splitted(relative_path = relative_path)
    splitted_list = [split]
    return splitted_list

    if int(vod.duration) < SPLIT_LENGTH or env_varz.WHSP_IS_BIG_FILES_ENABLED == "False":
        split = Splitted(relative_path = relative_path)
        splitted_list = [split]
        return splitted_list

    command = [
        "ffmpeg",
        "-i", relative_path,
        "-af", f"silencedetect=noise=-{noise_vol}:d={duration}",
        "-f", "null", "-"
    ]
    logger.debug("doing shit command:" + str(command))
    
    silence_output_raw = _execSubprocCmd(command)

    silence_list: List[Silence] = parse_silence_data(silence_output_raw)

    ############
    # SPLIT IT #
    ############
    quotient = int(vod.duration) // SPLIT_LENGTH
    remainder = int(vod.duration) % SPLIT_LENGTH

    logger.debug("quotient " + str( quotient))
    logger.debug("remainder " + str( remainder))

    splitted_list: List[Splitted] = [] # FAZEATHON_part0_.opus, FAZEATHON_part2_.opus, FAZEATHON_part3_.opus ....

    silences_of_split: List[Silence] = []

    for i in range(quotient):
        logger.debug('~~~~~~~~~')
        _bisect_silence_trick = Silence()
        _bisect_silence_trick.start = SPLIT_LENGTH * (i+1)
        index = bisect.bisect_left(silence_list, _bisect_silence_trick)
        # silences_of_split.append(silence_list[index])

        silences_of_split.append(silence_list[index])

        logger.debug(f"{i}, {(SPLIT_LENGTH * (i+1))}")
        logger.debug(f"silence_list[{index}]: {silence_list[index]}")

    # THIS CAN BE BETTER
    # step of 2, b/c the lines looks like: -------> # 1. silenncedectect @ start: 12.2s
    for i in range(0, len(silences_of_split), 2):   # 2. silenncedectect @ end: 23.1s
        output_path = get_filename_stupidly_(relative_path, i)
        splitted: Splitted = cut_the_file(i, silences_of_split, vod, relative_path, output_path)
        splitted_list.append(splitted)

    return splitted_list

def get_filename_stupidly_(filename, count):
    last_dot_index = filename.rfind('.')
    filename_new = f"{filename[:last_dot_index]}_part{count}_{filename[last_dot_index:]}"
    return filename_new


def cut_the_file(i, silences_of_split: List[Silence] , vod: Vod, input_file, output_file) -> Splitted:
    if i == 0:
        start = 0
        end = int(silences_of_split[0].start + 2) # arbitray 2s offset
    elif i >= (len(silences_of_split) - 1):
        start = int(silences_of_split[i].start)
        end = int(vod.duration)
    else:
        start = int(silences_of_split[i].start)
        end = int(silences_of_split[i+1].start + 2) # arbitray 2s offset, again

    # sometimes there is no silence where we want it to be
    #
    #    s[i]                                           s[i+1]
    #      ↓                                             ↓     
    #    12000s -------------------------------------- 39000s     <------------ THIS IS NOT GOOD
    #    12000s -------- <4 hours> ------- 26400
    if ((start + SPLIT_LENGTH) < end): # prob can fix in future at "this can be better" line above
        start_extended = start + SPLIT_LENGTH
        end = start_extended
        if i < (len(silences_of_split) - 1):
            silences_of_split[i+1].start = start_extended
        if end > int(vod.duration):
            end = int(vod.duration)

    logger.debug(f'cutting the file @  {start} to {(end)}' )

    try:
        # ffmpeg -ss 106200 -i input_file  -to 145500 -c copy output_file
        command = [
            "ffmpeg",
            "-ss", str(start), # order is import, need -ss before -i. Makes fast.
            "-i", input_file,
            "-to", str(end),
            "-c", "copy", output_file,
            "-y",
        ]
        logger.debug("command")
        logger.debug(str(command))
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()  

        logger.debug("process.returncode (0 is good): " + str(process.returncode))
        if process.returncode == 0:
            splitted = Splitted(duration = (end - start), relative_path = output_file)
            return splitted
        else:
            output = stdout.splitlines() + stderr.splitlines()
            logger.debug(output)
            raise Exception('shiiiiit failed file split')
    except subprocess.CalledProcessError as e:
        logger.error("Failed to run ffmpeg command:")
        logger.error(e)
        traceback.print_exc()
        return False

# This code is sorta duplicated. It is in Downloader too
def _execSubprocCmd(command):
    logger.debug('doing some shit........')
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()  

        logger.debug("process.returncode (0 is good): " + str(process.returncode))
        if process.returncode == 0:
            output = stdout.splitlines() + stderr.splitlines()
            return output
        else:
            raise Exception('shiiiiit failed file split')
    except subprocess.CalledProcessError as e:
        logger.error("Failed to run ffmpeg command:")
        logger.error(e)
        traceback.print_exc()
        return False

def parse_silence_data(silence_output):
    # EXAMPLE_INPUT = [
    #     "[silencedetect @ 0000025bc8bef000] silence_start: 30049.6",
    #     "[silencedetect @ 0000025bc8bef000] silence_end: 30068.2 | silence_duration: 18.6497",
    #     "size=N/A time=11:12:15.09 bitrate=N/A speed=1.27e+03x",
    #     "size=N/A time=11:12:15.09 bitrate=N/A speed=1.27e+03x",
    #     "size=N/A time=11:12:15.09 bitrate=N/A speed=1.27e+03x",
    #     "[silencedetect @ 0000025bc8bef000] silence_start: 30862.9",
    #     "[silencedetect @ 0000025bc8bef000] silence_end: 30876 | silence_duration: 13.0282",
    # ]
    silence_start_pattern = re.compile(r"silence_start: (\d+\.?\d*)")
    silence_end_pattern = re.compile(r"silence_end: (\d+\.?\d*)")
    silence_duration_pattern = re.compile(r"silence_duration: (\d+\.?\d*)")

    silences = []

    current_silence = {}

    silence_iter = iter(silence_output)
    for line in silence_iter:
        start_match = silence_start_pattern.search(line)

        if start_match:
            silence_curent = Silence()
            # current_silence = { 
            #     'start': None,
            #     'end': None,
            #     'duration': None,
            # }
            # current_silence['start'] = float(start_match.group(1))
            silence_curent.start = float(start_match.group(1))

            # pro trick next line
            # logger.debug(line)
            line = next(silence_iter)
            while "size=" in line and "bitrate=" in line:
                line = next(silence_iter)
            # logger.debug(line)

            end_match = silence_end_pattern.search(line)
            duration_match = silence_duration_pattern.search(line)

            if end_match:
                # current_silence['end'] = float(end_match.group(1))
                silence_curent.end = float(end_match.group(1))
            if duration_match:
                # current_silence['duration'] = float(silence_match.group(1))
                silence_curent.duration = float(duration_match.group(1))
            # silences.append(current_silence)
            silences.append(silence_curent)

    # logger.debug("YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    # for s in silences:
    #     logger.debug(s)
    # logger.debug("YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA2")
    return silences

def parse_silence_data_Xtest(vod, silence_output_raw, rel_path):
    silence_list: List[Silence] = parse_silence_data(silence_output_raw)
    # split_files(vod, silence_list, rel_path)

