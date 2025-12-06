import threading
import queue
import math
import os
import select
import time
import boto3
import subprocess

import botocore

s3 = boto3.client("s3")

bucket    = "my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket"
key_small = "channels/vod-audio/caedrel/2510842357/BUDAPEST_MAJOR_-_FAZE_ELIMINATION-v2629297105.mp4"
key_big   = "channels/vod-audio/caedrel/2510842357/DROPS_NUT_RAIDERS_TESTICULAR_TORSION_TUESDAY_EXPEDITION_TIME_BUNGULATE-v2628130294.mp4"

key = key_big
output_key = key.replace(".mp4", "_420_CLAUDE_MAGIC.opus")
chunk_size = 10 * 1024 * 1024  # 1MB or whatever works
max_chunk = chunk_size * 2
start = 0


# Stream chunk to ffmpeg
ffmpeg = subprocess.Popen(
    [
            'ffmpeg',
            '-i', 'pipe:0',  # Input from stdin
            '-c:a', 'libopus',
            '-ac', '1',  # Mono
            '-ar', '16000',  # 16kHz sample rate
            '-b:a', '10K',  # 10 kbps bitrate
            '-vbr', 'constrained',
            '-application', 'voip',
            '-compression_level', '5',
            '-f', 'opus',  # Essential for streaming # or 'ogg' or 'webm'
            '-vn',  # No video
            'pipe:1'  # Output to stdout
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,  # <-- capture logs
    bufsize=0
)


processed_data = b""

# Create the multipart upload
mpu = s3.create_multipart_upload(Bucket=bucket, Key=output_key)
parts = []

part_number = 1

total_proccess = 0
total_s3_dl = 0



def write_to_ffmpeg(ffmpeg_proc, s3_client, bucket, key, chunk_size):
    """Thread to download from S3 and feed to ffmpeg"""
    start = 0
    while True:
        range_header = f"bytes={start}-{start + chunk_size - 1}"
        try:
            resp = s3_client.get_object(Bucket=bucket, Key=key, Range=range_header)
            raw_bytes = resp["Body"].read()
            if not raw_bytes:
                break
            ffmpeg_proc.stdin.write(raw_bytes)
            ffmpeg_proc.stdin.flush()
            start += chunk_size
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidRange':
                break
            raise
    ffmpeg_proc.stdin.close()

def read_from_ffmpeg(ffmpeg_proc, output_queue):
    """Thread to read from ffmpeg and queue for upload"""
    while True:
        chunk = ffmpeg_proc.stdout.read(5 * 1024 * 1024)  # 5MB chunks
        if not chunk:
            break
        output_queue.put(chunk)
    output_queue.put(None)  # Sentinel

# Main code
output_queue = queue.Queue(maxsize=10)

# Start threads
write_thread = threading.Thread(
    target=write_to_ffmpeg,
    args=(ffmpeg, s3, bucket, key, chunk_size)
)
read_thread = threading.Thread(
    target=read_from_ffmpeg,
    args=(ffmpeg, output_queue)
)




part_buffer = b""
MIN_PART_SIZE = 5 * 1024 * 1024  # 5MB minimum for S3


write_thread.start()
read_thread.start()


def upload_some_parts():
    # if part_buffer:
    global part_number, part_buffer, parts
    print(f'Uploading final part {part_number}, size={len(part_buffer)}')
    part_resp = s3.upload_part(
        Bucket=bucket,
        Key=output_key,
        PartNumber=part_number,
        UploadId=mpu["UploadId"],
        Body=part_buffer
    )
    parts.append({"ETag": part_resp["ETag"], "PartNumber": part_number})
    part_number += 1
    time.sleep(10)
    
shitcount = 0
while True:
    chunk_ff_out = output_queue.get()
    if chunk_ff_out is None:  # Done
        upload_some_parts()
        # Upload any remaining data as the final part
        break
    # print('reading...', len(chunk_ff_out))
    if shitcount % 10 == 1:
        print(f"{shitcount}: reading... ff_out bytez {len(chunk_ff_out)} - len(part_buffer)={len(part_buffer)}")

    ### 💣 BOOM ###
    part_buffer += chunk_ff_out

    # if len(chunk_ff_out) > 0:
    if len(part_buffer) >= MIN_PART_SIZE:
        upload_some_parts()
        part_buffer = b""
    shitcount += 1
    # time.sleep(5)
write_thread.join()

ffmpeg.stdin.close() if not ffmpeg.stdin.closed else None  # Make sure stdin is closed

read_thread.join()
ffmpeg.wait()

print("gg we complete it now")
# Complete multipart upload
print("parts")
print(parts)

# Handle edge case: if entire file is < 5MB, use regular upload instead
if not parts:
    print("File too small for multipart, aborting and using regular upload")
    s3.abort_multipart_upload(
        Bucket=bucket,
        Key=output_key,
        UploadId=mpu["UploadId"]
    )
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=part_buffer
    )
else:
    s3.complete_multipart_upload(
        Bucket=bucket,
        Key=output_key,
        UploadId=mpu["UploadId"],
        MultipartUpload={"Parts": parts},
    )
