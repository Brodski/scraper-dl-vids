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
output_key = key.replace(".mp4", "_420_CHATGPT_MAGIC.opus")
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


while True:
    range_header = f"bytes={start}-{start + chunk_size - 1}"
    # if part_number % 10 == 0  or part_number >1730:
    if True:
        print("------------------------")
        print(f"--- {range_header}  ---")
        print("------------------------")
    try:
        resp = s3.get_object(Bucket=bucket, Key=key, Range=range_header)
    except botocore.exceptions.ClientError as e:
        print(resp)
        if e.response['Error']['Code'] == 'InvalidRange':
            break
        else:
            raise
    # print("resp")
    # print(resp)
    content_length = resp["ContentLength"]
    chunk_data = resp["Body"]
    raw_bytes = chunk_data.read()
    if not raw_bytes:
        print("WTF")
        break

    print("writing.......")
    if True:
        print(f"IN: Chunk {part_number} processed, size={len(raw_bytes)} bytes")
        # print(f"raw_bytes: {raw_bytes[0]}")
        # print(f"raw_bytes: {raw_bytes[-1]}")
        print(f"First 10 bytes: {raw_bytes[:10]}")
        print(f"Last 10 bytes: {raw_bytes[-10:]}")


    stdin_fd = ffmpeg.stdin.fileno()
    stdout_fd = ffmpeg.stdout.fileno()
    stderr_fd = ffmpeg.stderr.fileno()

    rlist, wlist, _ = select.select([stdout_fd, stderr_fd], [stdin_fd], [])
    os.set_blocking(stdin_fd, False)
    os.set_blocking(stdout_fd, False)
    print('shiiiiiiit')
    if stdin_fd in wlist:
        n = os.write(stdin_fd, raw_bytes[:])
        print("n, idk", n)
    
    print(f"IN: Chunk {part_number} processed, size={len(raw_bytes)} bytes")
    time.sleep(1)



    print("2 reading.......")
    # Read all available data from ffmpeg stdout
    chunk_ff_out = b""
    while True:
        try:
            data = os.read(stdout_fd, max_chunk)
            if not data:
                break
            chunk_ff_out += data
        except BlockingIOError:
            # No more data available right now
            break
        except OSError as e:
            print(f"Read error: {e}")
            break

    if not chunk_ff_out:
        time.sleep(0.5)  # Give ffmpeg time to process
        try:
            chunk_ff_out = os.read(stdout_fd, max_chunk)
        except BlockingIOError:
            chunk_ff_out = b""



    # chunk_ff_out = os.read(stdout_fd, max_chunk) # reads at most "max_chunk" bytes


    total_proccess    += len(chunk_ff_out)
    total_s3_dl       += len(raw_bytes)
    total_proccess_MB  = math.floor(total_proccess / 1_048_576)
    total_s3_dl_MB     = math.floor(total_s3_dl / 1_048_576)

    # if part_number % 10 == 0  or part_number >1730:
    if True:
        print(f"OUT {part_number} chunk_ff_out bytes: ",  len(chunk_ff_out))
        print(f"TOTAL IN:total_s3_dl: {total_s3_dl} = {total_s3_dl_MB} MB")
        print(f"TOTAL OUT:total_proccess: {total_proccess} = {total_proccess_MB} MB")


    # Upload processed chunk as multipart part
    part_resp = s3.upload_part(
        Bucket=bucket,
        Key=output_key,
        PartNumber=part_number,
        UploadId=mpu["UploadId"],
        Body=chunk_ff_out
    )
    # if part_number % 10 == 0  or part_number >1730:
    if True:
        print("part_resp")
        print(part_resp)
    parts.append({"ETag": part_resp["ETag"], "PartNumber": part_number})

    part_number += 1
    start += chunk_size
    time.sleep(1)

print("gg we complete it now")
# Complete multipart upload
print("parts")
print(parts)
s3.complete_multipart_upload(
    Bucket=bucket,
    Key=output_key,
    UploadId=mpu["UploadId"],
    MultipartUpload={"Parts": parts},
)
