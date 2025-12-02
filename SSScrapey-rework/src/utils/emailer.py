from collections import Counter
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
        self.vod: Vod            = kwargs.get("vod")

        self.msg               = kwargs.get("msg")
        self.status: Status    = kwargs.get("status") # also is type "Errorz" from download
        self.device            = kwargs.get("device")
        self.whsp_lang         = kwargs.get("whsp_lang")

        self.runtime_model_ts  = kwargs.get("runtime_model_ts")
        self.runtime_ts        = kwargs.get("runtime_transcribe")
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


def write_transcriber_email(metadata_arr: List[MetadataShitty], completed_uploaded_tscripts, elapsed_time):
    total = env_varz.TRANSCRIBER_VODS_PER_INSTANCE
    status_counter = Counter()

    msg_lines = []
    seconds = int(elapsed_time)
    mins    = seconds / 60
    hours   = mins / 60
    msg_lines.append(f"TOTAL TIME: {seconds:.2f} secs = {mins:.2f} min = {hours:.2f} hours")
    msg_lines.append("\n")

    #################
    ### GPU & CPU ###
    #################
    logical_cores, gpu_name, total_vram, cpu_manufacturer, cpu_model, cpu_frequency_mhz, cpu_cache = extra_data_about_instance()
    msg_lines.append(
        f"gpu_name: {gpu_name}\n"
        f"logical_cores: {logical_cores}\n"
        f"total_vram: {total_vram}\n"
        f"cpu_manufacturer: {cpu_manufacturer}\n"
        f"cpu_model: {cpu_model}\n"
        f"cpu_frequency_mhz: {cpu_frequency_mhz}\n"
        f"cpu_cache: {cpu_cache}\n"
    )

    ############
    ### VODS ###
    ############
    for idx, metadata in enumerate(metadata_arr):
        metadata: MetadataShitty = metadata

        status          = metadata.status
        status_counter[status] += 1
        
        vod: Vod        = metadata.vod
        vod_id          = vod.id                    if vod else "(no vod)"
        vod_title       = vod.title                 if vod else "(no vod)"
        channel         = vod.channels_name_id      if vod else "(no vod)"
        runtime_ffmpeg_dl = int(metadata.runtime_ffmpeg_dl) if metadata.runtime_ffmpeg_dl else 0
        runtime_dl        = int(metadata.runtime_dl)        if metadata.runtime_dl else 0
        runtime_model_ts  = int(metadata.runtime_model_ts)  if metadata.runtime_model_ts else 0
        runtime_ts        = int(metadata.runtime_ts)        if metadata.runtime_ts else 0
        transcript_url    = None
        for t in completed_uploaded_tscripts:
            try:
                if t.endswith(".json"):
                    transcript_url = t
            except:
                print("oops, .endswith() is not a real method")
        msg_lines.append(
            f"-------------{idx}--------------\n"
            f"Status: {status}\n"
            f"Channel ID: {channel}\n"
            f"VOD Title: {vod_title}\n"
            f"VOD ID: {vod_id}\n"
            f"Vod Duration: {vod.duration_string}\n"
            f"Model load time: {runtime_model_ts}s\n"
            f"Transcription time: {runtime_ts}s\n"
            f"Whisper Lang: {metadata.whsp_lang}\n"
            f"Device: {metadata.device}\n"
            f"Transcript @: {transcript_url}\n"
            f"Message: {metadata.msg}\n"
        )
    summary_lines = ["Transcriber Report Summary:", f"Total expected items: {total}", f"Total actual item {str(len(metadata_arr))}"]
    for status, count in status_counter.items():
        summary_lines.append(f"{status}: {count}")

    # Combine summary and detailed report
    cli = find_aws_logging_info_transcriber()
    report_message = "\n".join(summary_lines + [""] + msg_lines)
    report_message = report_message + "\n" + cli

    sendEmail(f"Transcriber {env_varz.ENV} report", report_message)
    logger.info(report_message)
    # logger.debug(f"Going to download: {vod.channels_name_id} - {vod.id} - title: {vod.title}")



##############
# SEND EMAIL #
# i vibe coded this
##############
from collections import Counter
def write_downloader_report(metadata_array_global, elapsed_time=0):
    total = env_varz.DWN_BATCH_SIZE
    status_counter = Counter()

    msg_lines = []
    seconds = int(elapsed_time)
    mins    = seconds / 60
    hours   = mins / 60
    msg_lines.append(f"TOTAL TIME: {seconds:.2f} secs = {mins:.2f} min = {hours:.2f} hours")
    msg_lines.append("\n")
    for idx, metadata in enumerate(metadata_array_global):
        status = getattr(metadata, 'status', 'N/A')
        status_counter[status] += 1

        message         = getattr(metadata, 'msg', '')
        channel         = getattr(metadata, 'channelId', 'Unknown')
        vod_id          = getattr(metadata, 'vodId', 'Unknown')
        vod_title       = getattr(metadata, 'vodTitle', 'Untitled')
        duration_string = getattr(metadata, 'duration_string', 'NA')
        runtime_ffmpeg_dl  = metadata.runtime_ffmpeg_dl or -69
        runtime_dl      = metadata.runtime_dl or -69
        
        runtime_ffmpeg_dl if runtime_ffmpeg_dl else 0
        runtime_dl if runtime_dl else 0

        msg_lines.append(
            f"-------------{idx}--------------\n"
            f"Status: {status}\n"
            f"Channel ID: {channel}\n"
            f"VOD Title: {vod_title}\n"
            f"VOD ID: {vod_id}\n"
            f"Duration: {duration_string}\n"
            f"runtime_ffmpeg_dl (sec): {float(runtime_ffmpeg_dl):.2f}\n"
            f"runtime_dl (sec): {float(runtime_dl):.2f}\n"
            f"Message: {message}\n"
        )

    # Build summary
    summary_lines = ["Download Report Summary:", f"Total expected items: {total}", f"Total actual item {str(len(metadata_array_global))}"]
    for status, count in status_counter.items():
        summary_lines.append(f"{status}: {count}")

    # Combine summary and detailed report
    cli = find_aws_logging_info()
    report_message = "\n".join(summary_lines + [""] + msg_lines)
    report_message = report_message + "\n" + cli

    sendEmail(f"Downloader {env_varz.ENV} report", report_message)
    logger.info(report_message)
    # logger.debug(f"Going to download: {vod.channels_name_id} - {vod.id} - title: {vod.title}")

