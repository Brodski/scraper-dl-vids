import os
import select
import sys
import time
import boto3
import subprocess
import threading
import queue

def stream_s3_through_ffmpeg(
    source_bucket, source_key,
    dest_bucket, dest_key,
    chunk_size=10*1024*1024  # 10MB chunks
):
    s3 = boto3.client('s3')
    
    # Start multipart upload
    mpu = s3.create_multipart_upload(Bucket=dest_bucket, Key=dest_key)
    upload_id = mpu['UploadId']
    is_windows = sys.platform == 'win32'
    # is_windows = False
    # ff_big_dick = (['wsl'] if is_windows else []) + [
    ff_big_dick =        [ 'ffmpeg',
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
    ]
    # Start ffmpeg subprocess
    print(ff_big_dick)
    ffmpeg_process = subprocess.Popen(ff_big_dick,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0
    )
    
    parts = []
    part_number = 1
    upload_buffer = b''
    min_part_size = 5*1024*1024  # S3 requires min 5MB per part (except last)
    
    def write_to_ffmpeg():
        """Thread: Download from S3 and write to ffmpeg stdin"""
        try:
            # Stream download from S3
            response = s3.get_object(Bucket=source_bucket, Key=source_key)
            stream = response['Body']
            
            for chunk in stream.iter_chunks(chunk_size=chunk_size):
                print('got a chunk...')
                ffmpeg_process.stdin.write(chunk)
                ffmpeg_process.stdin.flush()
            print("closing")
            ffmpeg_process.stdin.close()  # Signal EOF to ffmpeg
        except Exception as e:
            print(f"Download error: {e}")
            ffmpeg_process.kill()
    
    # Start download thread
    download_thread = threading.Thread(target=write_to_ffmpeg, daemon=True)
    download_thread.start()
    
    try:
        # Read compressed output from ffmpeg and upload to S3
        # while True:
        print("ffmpeg_process.poll(): ", ffmpeg_process.poll())
        print("ffmpeg_process.poll(): ", ffmpeg_process.poll())
        print("ffmpeg_process.poll(): ", ffmpeg_process.poll())
        print("ffmpeg_process.poll(): ", ffmpeg_process.poll())
        dick = select.select([], [], [], 3)
        dick2 = select.select([ffmpeg_process.stdout.fileno()], [], [], 3)
        print(dick)
        print(dick2)
        time.sleep(3)
        # print("select.select([ffmpeg_process.stdout], [], [], 0): ", select.select([ffmpeg_process.stdout.fileno()], [], [], 0)[0])
        while ffmpeg_process.poll() is None or select.select([ffmpeg_process.stdout.fileno()], [], [], 3)[0]:

            print('reading chunk...')
            readable, _, _ = select.select([ffmpeg_process.stdout.fileno()], [], [], 5.1)
            if not readable:
                continue
            
            print('reading os...')
            # Read available data (up to chunk_size)
            chunk = os.read(ffmpeg_process.stdout.fileno(), chunk_size)
            size_in_bytes = len(chunk)
            print(size_in_bytes)
            time.sleep(5)
            if not chunk:
                print("EOF !!! ")
                break  # EOF



            # print("reading a chunk...")
            # chunk = ffmpeg_process.stdout.read(chunk_size)
            # print("post reading....")
            # if not chunk:
            #     break  # ffmpeg finished
            print("min_part_size:", min_part_size)
            print("len(upload_buffer):", len(upload_buffer))
            upload_buffer += chunk
            
            # Upload when we have enough data (or it's the last chunk)
            if len(upload_buffer) >= min_part_size:
                print('doing some upload shit...')
                part = s3.upload_part(
                    Bucket=dest_bucket,
                    Key=dest_key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=upload_buffer
                )
                parts.append({
                    'PartNumber': part_number,
                    'ETag': part['ETag']
                })
                print(f"Uploaded part {part_number}, size: {len(upload_buffer)} bytes")
                part_number += 1
                upload_buffer = b''
        
        # Upload final part if any data remains
        if upload_buffer:
            print('doing up load_buffer shit ...')
            part = s3.upload_part(
                Bucket=dest_bucket,
                Key=dest_key,
                PartNumber=part_number,
                UploadId=upload_id,
                Body=upload_buffer
            )
            parts.append({
                'PartNumber': part_number,
                'ETag': part['ETag']
            })
            print(f"Uploaded final part {part_number}, size: {len(upload_buffer)} bytes")
        
        # Complete multipart upload
        s3.complete_multipart_upload(
            Bucket=dest_bucket,
            Key=dest_key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        
        # Wait for ffmpeg to finish
        ffmpeg_process.wait()
        download_thread.join()
        
        print(f"Successfully processed and uploaded: {dest_key}")
        print(f"Total parts uploaded: {len(parts)}")
        
    except Exception as e:
        # Abort multipart upload on error
        s3.abort_multipart_upload(
            Bucket=dest_bucket,
            Key=dest_key,
            UploadId=upload_id
        )
        print(f"Error: {e}")
        ffmpeg_process.kill()
        raise

# Example usage
if __name__ == '__main__':

    bucket    = "my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket"
    key_small = "channels/vod-audio/caedrel/2510842357/BUDAPEST_MAJOR_-_FAZE_ELIMINATION-v2629297105.mp4"
    key_big   = "channels/vod-audio/caedrel/2510842357/DROPS_NUT_RAIDERS_TESTICULAR_TORSION_TUESDAY_EXPEDITION_TIME_BUNGULATE-v2628130294.mp4"
    keyzzzz = key_small
    dest = keyzzzz.replace(".mp4", "CLAUDE_2.mp4")
    stream_s3_through_ffmpeg(
        source_bucket=bucket,
        source_key=key_big,
        dest_bucket=bucket,
        dest_key=dest,
        chunk_size=10*1024*1024  # 10MB chunks
    )