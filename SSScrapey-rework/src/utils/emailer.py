from collections import Counter
import os
import traceback
from typing import List
import boto3

import logging
from utils.logging_config import LoggerConfig
from utils.ecs_meta import find_aws_logging_info
from utils.ecs_meta import find_aws_logging_info_transcriber

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()

def sendEmail(subject, body):
    ses = boto3.client('ses', region_name='us-east-1')

    # Send the email
    response = ses.send_email(
        Source='noreply@dev-captions.bski.one', # TODO update "dev"-catpions
        Destination={
            'ToAddresses': [
                'loganwallace.smash@gmail.com',
            ],
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': 'UTF-8'
                }
            }
        }
    )
    # print(response)
    # print("Email sent: " + subject)

from enum import Enum
from models.Vod import Vod
from env_file import env_varz

class Status(Enum):
    FAILED = "failed"
    SUCCESS = "success"
    NOTHING_TODO = "nothing_todo"

class MetadataShitty:
    def __init__(self, **kwargs):
        self.vod: Vod           = kwargs.get("vod")

        self.msg               = kwargs.get("msg")
        self.status: Status    = kwargs.get("status") # also is type "Errorz" from download
        self.device            = kwargs.get("device")
        self.whsp_lang         = kwargs.get("whsp_lang")

        self.runtime_model_ts  = kwargs.get("runtime_model_ts")
        self.runtime_ts        = kwargs.get("runtime_ts")
        self.runtime_ffmpeg_dl = kwargs.get("runtime_ffmpeg_dl")
        self.runtime_dl        = kwargs.get("runtime_dl")

def extra_data_about_instance():
    import torch
    import os

    logical_cores = ""
    gpu_name = ""
    total_vram = ""
    cpu_manufacturer = ""
    cpu_model = ""
    cpu_frequency_mhz = ""
    cpu_cache = ""
    ### Vendor / manufacturer ###
    try:
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if ":" in line:
                        key, value = map(str.strip, line.split(":", 1))
                        if key == "vendor_id":
                            cpu_manufacturer = value
                        elif key == "model name":
                            cpu_model = value
                        elif key == "cpu MHz":
                            cpu_frequency_mhz = float(value)
                        elif key == "cache size":
                            cpu_cache = value
        except:
            pass

        logical_cores = os.cpu_count()
        gpu_name      = torch.cuda.get_device_name(0)
        deviceX       = torch.device("cuda:0")
        total_vram    = torch.cuda.get_device_properties(deviceX).total_memory

        print("VRAM (bytes):", total_vram)
        print("VRAM (GB):", total_vram / 1024**3)
    except Exception as e:
        stack_trace = traceback.format_exc()
        error_message = f"ERROR Transcribing vod: {e}"
        logger.error(error_message + "\n" + stack_trace)

    return logical_cores, gpu_name, total_vram, cpu_manufacturer, cpu_model, cpu_frequency_mhz, cpu_cache


# def write_transcriber_email(metadata_arr: List[MetadataShitty], completed_uploaded_tscripts, elapsed_time):
#     total = env_varz.TRANSCRIBER_VODS_PER_INSTANCE
#     status_counter = Counter()

#     msg_lines = []
#     total_ts_seconds = int(elapsed_time)
#     total_ts_mins    = total_ts_seconds / 60
#     total_ts_hours   = total_ts_mins / 60
#     vod_total_seconds = 0
#     msg_lines.append(f"TOTAL TIME: {total_ts_seconds:.2f} secs = {total_ts_mins:.2f} min = {total_ts_hours:.2f} hours")
#     msg_lines.append("\n")
    
#     #################
#     ### GPU & CPU ###
#     #################
#     logical_cores, gpu_name, total_vram, cpu_manufacturer, cpu_model, cpu_frequency_mhz, cpu_cache = extra_data_about_instance()
#     msg_lines.append("**************")
#     msg_lines.append(
#         f"💣 BOOM 💣 gpu_name: {gpu_name}\n"
#         f"logical_cores: {logical_cores}\n"
#         f"total_vram: {total_vram}\n"
#         f"cpu_manufacturer: {cpu_manufacturer}\n"
#         f"cpu_model: {cpu_model}\n"
#         f"cpu_frequency_mhz: {cpu_frequency_mhz}\n"
#         f"cpu_cache: {cpu_cache}\n"
#     )
#     msg_lines.append("**************")

#     ############
#     ### VODS ###
#     ############
#     for idx, metadata in enumerate(metadata_arr):
#         metadata: MetadataShitty = metadata
#         if metadata.vod and metadata.vod.duration:
#             vod_total_seconds = vod_total_seconds + int(metadata.vod.duration)

#         status          = metadata.status
#         status_counter[status] += 1
        
#         vod: Vod        = metadata.vod
#         vod_id          = vod.id                    if vod else "(no vod)"
#         vod_title       = vod.title                 if vod else "(no vod)"
#         channel         = vod.channels_name_id      if vod else "(no vod)"
#         runtime_ffmpeg_dl = int(metadata.runtime_ffmpeg_dl) if metadata.runtime_ffmpeg_dl else 0
#         runtime_dl        = int(metadata.runtime_dl)        if metadata.runtime_dl else 0
#         runtime_model_ts  = int(metadata.runtime_model_ts)  if metadata.runtime_model_ts else 0
#         runtime_ts        = int(metadata.runtime_ts)        if metadata.runtime_ts else 0
#         transcript_url    = None
#         for t in completed_uploaded_tscripts:
#             if t.endswith(".json"):
#                 transcript_url = t
#         msg_lines.append(
#             f"-------------{idx}--------------\n"
#             f"Status: {status}\n"
#             f"Channel ID: {channel}\n"
#             f"VOD Title: {vod_title}\n"
#             f"VOD ID: {vod_id}\n"
#             f"Vod Duration: {vod.duration_string}\n"
#             f"Model load time: {runtime_model_ts}s\n"
#             f"Transcription time: {runtime_ts}s\n"
#             f"Whisper Lang: {metadata.whsp_lang}\n"
#             f"Device: {metadata.device}\n"
#             f"Transcript @: {transcript_url}\n"
#             f"Message: {metadata.msg}\n"
#         )
#     total_vod_seconds = int(vod_total_seconds)
#     total_vod_mins    = total_vod_seconds / 60
#     total_vod_hours   = total_vod_mins / 60
    
#     average_runtime = int(vod_total_seconds / total_ts_seconds) if total_ts_seconds != 0 else -1
#     average_mins = average_runtime / 60
#     average_hours = average_mins / 60

#     total_msg = f"total_vod_seconds={total_vod_seconds:.2f} sec = {total_vod_mins:.2f} min = {total_vod_hours:.2f} hours"

#     avg_msg = f"Vod-total-time to transcriber-total-time ratio (vod_total_seconds / total_ts_seconds) = {average_runtime:.2f} sec = {average_mins:.2f} min = {average_hours:.2f}"

#     summary_lines = ["Transcriber Report Summary:", f"Total expected items: {total}", f"Total actual item {str(len(metadata_arr))}"]
#     summary_lines.append(total_msg)
#     summary_lines.append(avg_msg)
#     for status, count in status_counter.items():
#         summary_lines.append(f"{status}: {count}")

#     # Combine summary and detailed report
#     cli = find_aws_logging_info_transcriber()
#     report_message = "\n".join(summary_lines + [""] + msg_lines)
#     report_message = report_message + "\n" + cli

#     sendEmail(f"Transcriber {env_varz.ENV} report", report_message)
#     logger.info(report_message)
#     # logger.debug(f"Going to download: {vod.channels_name_id} - {vod.id} - title: {vod.title}")



##############
# SEND EMAIL #
# i vibe coded this
##############
# from collections import Counter
# def write_downloader_report(metadata_array_global: List[MetadataShitty], elapsed_time=0):
#     total = env_varz.DWN_BATCH_SIZE
#     status_counter = Counter()

#     msg_lines = []
#     seconds = int(elapsed_time)
#     mins    = seconds / 60
#     hours   = mins / 60

#     vod_total_seconds = 0

#     msg_lines.append(f"TOTAL TIME: {seconds:.2f} secs = {mins:.2f} min = {hours:.2f} hours")
#     msg_lines.append("\n")
#     for idx, metadata in enumerate(metadata_array_global):
#         status = getattr(metadata, 'status', 'N/A')
#         status_counter[status] += 1

#         message         = getattr(metadata, 'msg', '')
#         channel         = getattr(metadata, 'channelId', 'Unknown')
#         vod_id          = getattr(metadata, 'vodId', 'Unknown')
#         vod_title       = getattr(metadata, 'vodTitle', 'Untitled')
#         duration_string = getattr(metadata, 'duration_string', 'NA')
#         vod             = getattr(metadata, 'vod', None)
#         runtime_ffmpeg_dl  = metadata.runtime_ffmpeg_dl or -69
#         runtime_dl      = metadata.runtime_dl or -69
        
#         runtime_ffmpeg_dl if runtime_ffmpeg_dl else 0
#         runtime_dl if runtime_dl else 0

#         if vod and vod.duration:
#             vod_total_seconds = vod_total_seconds + int(vod.duration)

#         msg_lines.append(
#             f"-------------{idx}--------------\n"
#             f"Status: {status}\n"
#             f"Channel ID: {channel}\n"
#             f"VOD Title: {vod_title}\n"
#             f"VOD ID: {vod_id}\n"
#             f"Duration: {duration_string}\n"
#             f"runtime_ffmpeg_dl (sec): {float(runtime_ffmpeg_dl):.2f}\n"
#             f"runtime_dl (sec): {float(runtime_dl):.2f}\n"
#             f"Message: {message}\n"
#         )



#     vod_total_mins    = vod_total_seconds / 60
#     vod_total_hours   = vod_total_mins / 60
    
#     average_runtime = int(vod_total_seconds / seconds) if seconds != 0 else -1
#     average_mins    = average_runtime / 60
#     average_hours   = average_mins / 60
#     total_msg       = f"total_seconds={vod_total_seconds:.2f} sec = {vod_total_mins:.2f} min = {vod_total_hours:.2f} hours"
    
#     avg_msg         = f"Vod-total-time to downloader-total-time ratio (vod_total_seconds / total_runtime) = {average_runtime:.2f} sec = {average_mins:.2f} min = {average_hours:.2f} hours"
    

#     # Build summary
#     summary_lines = ["Download Report Summary:", f"Total expected items: {total}", f"Total actual item {str(len(metadata_array_global))}"]
#     summary_lines.append(total_msg)
#     summary_lines.append(avg_msg)

#     for status, count in status_counter.items():
#         summary_lines.append(f"{status}: {count}")

#     # Combine summary and detailed report
#     cli = find_aws_logging_info()
#     report_message = "\n".join(summary_lines + [""] + msg_lines)
#     report_message = report_message + "\n" + cli

#     sendEmail(f"Downloader {env_varz.ENV} report", report_message)
#     logger.info(report_message)
#     # logger.debug(f"Going to download: {vod.channels_name_id} - {vod.id} - title: {vod.title}")



from collections import Counter
from typing import List, Callable, Optional

def format_time_units(seconds) -> tuple[float, float, float]:
    mins = seconds / 60
    hours = mins / 60
    return seconds, mins, hours

def calculate_vod_metrics(metadata_array: List[MetadataShitty]) -> tuple[int, Counter]:
    vod_total_seconds = 0
    status_counter = Counter()
    
    for metadata in metadata_array:
        status = getattr(metadata, 'status', 'N/A')
        status_counter[status] += 1
        
        vod = getattr(metadata, 'vod', None)
        if vod and vod.duration:
            vod_total_seconds += int(vod.duration)
    
    return vod_total_seconds, status_counter

# def format_time_message(label: str, seconds: float) -> str:
#     secs, mins, hours = format_time_units(seconds)
#     return f"{label}: {secs:.2f} secs = {mins:.2f} min = {hours:.2f} hours"

def build_summary_lines(report_type: str, total_expected: int, actual_count: int, vod_total_seconds: int, elapsed_time: float, status_counter: Counter) -> List[str]:
    # report_type --> Downloader or Transcriber
    
    vod_total_seconds = int(vod_total_seconds)
    elapsed_time      = elapsed_time if elapsed_time != 0 else -1  # divide by zero :O

    summary_lines = [
        f"{report_type} Report Summary:",
        f"Total expected items: {total_expected}",
        f"Total actual item {actual_count}"
    ]
    

    vod_total_secs, vod_total_mins, vod_total_hours = format_time_units(vod_total_seconds)

    average_runtime = vod_total_seconds / elapsed_time
    avg_secs, avg_mins, avg_hours = format_time_units(average_runtime)


    summary_lines.append(f"∑ Vod total hours = {vod_total_hours:.2f} hours = {vod_total_mins:.2f} min = {vod_total_secs:.2f} sec")
    summary_lines.append(f"📐 ratio = {avg_secs:.2f} vod secs per compute seconds")
    summary_lines.append(f"          = vod min / compute min = vod hours / compute hour")
    summary_lines.append(f"          = vod_total_seconds / total_runtime = {vod_total_seconds:.2f} / {elapsed_time:.2f}")
    summary_lines.append(f"          ---> (x seconds completed per 1 second of compute)")
    
    for status, count in status_counter.items():
        summary_lines.append(f"{status}: {count}")
    
    return summary_lines

def write_downloader_report(metadata_array_global: List[MetadataShitty], elapsed_time=-1):

    msg_lines = []
    
    for idx, metadata in enumerate(metadata_array_global):
        status            = getattr(metadata, 'status', 'N/A')
        message           = getattr(metadata, 'msg', '')
        channel           = getattr(metadata, 'channelId', 'Unknown')
        vod_id            = getattr(metadata, 'vodId', 'Unknown')
        vod_title         = getattr(metadata, 'vodTitle', 'Untitled')
        duration_string   = getattr(metadata, 'duration_string', 'NA')
        runtime_ffmpeg_dl = metadata.runtime_ffmpeg_dl or 0
        runtime_dl        = metadata.runtime_dl or 0

        msg_lines.append(
            f"-------------{idx}--------------\n"
            f"Status: {status}\n"
            f"Duration: {duration_string}\n"
            f"Channel ID: {channel}\n"
            f"VOD Title: {vod_title}\n"
            f"VOD ID: {vod_id}\n"
            f"runtime_ffmpeg_dl (sec): {float(runtime_ffmpeg_dl):.2f}\n"
            f"runtime_dl (sec): {float(runtime_dl):.2f}\n"
            f"Message: {message}\n"
        )

    elapsed_time      = int(elapsed_time) if elapsed_time is not None else -1
    secs, mins, hours = format_time_units(elapsed_time)
    heading_summary   = f"\n🔥🔥 TOTAL TIME: {secs:.2f} secs = {mins:.2f} min = {hours:.2f} hours🔥🔥\n"
    vod_total_seconds, status_counter = calculate_vod_metrics(metadata_array_global)

    summary_lines = build_summary_lines("Download", env_varz.DWN_BATCH_SIZE, len(metadata_array_global), vod_total_seconds, elapsed_time, status_counter)

    cli = find_aws_logging_info()
    report_message = "\n".join([heading_summary] + [""] + summary_lines + [""] + msg_lines) + "\n" + cli
    
    sendEmail(f"Downloader {env_varz.ENV} report", report_message)
    logger.info(report_message)

def write_transcriber_email(metadata_arr: List[MetadataShitty], completed_uploaded_tscripts, elapsed_time):


    msg_lines = []
    
    # GPU & CPU info
    logical_cores, gpu_name, total_vram, cpu_manufacturer, cpu_model, cpu_frequency_mhz, cpu_cache = extra_data_about_instance()
    msg_lines.extend([
        "******* GPU *******",
        f"💣 CONTAINER_ID! {os.getenv('CONTAINER_ID')} 💣"
        f"💣 BOOM 💣 gpu_name: {gpu_name}\n"
        f"logical_cores: {logical_cores}\n"
        f"total_vram: {total_vram}\n"
        f"cpu_manufacturer: {cpu_manufacturer}\n"
        f"cpu_model: {cpu_model}\n"
        f"cpu_frequency_mhz: {cpu_frequency_mhz}\n"
        f"cpu_cache: {cpu_cache}\n",
        "*******************"
    ])
    
    for idx, metadata in enumerate(metadata_arr):
        vod: Vod          = metadata.vod if metadata.vod is not None else Vod()
        vod_id            = vod.id      if vod else "(no vod)"
        vod_title         = vod.title   if vod else "(no vod)"
        channel           = vod.channels_name_id            if vod else "(no vod)"
        runtime_ffmpeg_dl = int(metadata.runtime_ffmpeg_dl) if metadata.runtime_ffmpeg_dl else 0
        runtime_dl        = int(metadata.runtime_dl)        if metadata.runtime_dl else 0
        runtime_model_ts  = int(metadata.runtime_model_ts) if metadata.runtime_model_ts else 0
        runtime_ts        = int(metadata.runtime_ts)        if metadata.runtime_ts else 0
        
        transcript_url = None
        for t in completed_uploaded_tscripts:
            if t.endswith(".json"):
                transcript_url = t
        
        msg_lines.append(
            f"-------------{idx}--------------\n"
            f"Status: {metadata.status}\n"
            f"Vod Duration: {vod.duration_string}\n"
            f"Total Transcription time: {runtime_model_ts + runtime_ts}s\n"     
            f"      Model load time: {runtime_model_ts}s\n"
            f"      Whisper transcription time: {runtime_ts}s\n"    
            f"Channel ID: {channel}\n"
            f"      VOD Title: {vod_title}\n"
            f"      VOD ID: {vod_id}\n"
            f"      Whisper Lang: {metadata.whsp_lang}\n"
            f"Device: {metadata.device}\n"
            f"Transcript @: {transcript_url}\n"
            f"Message: {metadata.msg}\n"
        )


    secs, mins, hours = format_time_units(elapsed_time)
    heading_summary = f"\n 🔥🔥TOTAL TIME: {secs:.2f} secs = {mins:.2f} min = {hours:.2f} hours 🔥🔥\n"

    vod_total_seconds, status_counter = calculate_vod_metrics(metadata_arr)
    
    summary_lines = build_summary_lines("Transcriber", env_varz.TRANSCRIBER_VODS_PER_INSTANCE, len(metadata_arr), vod_total_seconds, elapsed_time, status_counter)

    cli = find_aws_logging_info_transcriber()
    report_message = "\n".join([heading_summary] + [""] + summary_lines + [""] + msg_lines) + "\n" + cli
    
    sendEmail(f"Transcriber {env_varz.ENV} report", report_message)
    logger.info(report_message)