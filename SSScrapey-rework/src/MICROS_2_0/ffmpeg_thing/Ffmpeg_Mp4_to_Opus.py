import os
import threading
import queue
import subprocess
import time
import boto3
import botocore


class Ffmpeg_Mp4_to_Opus:
    def __init__(self, bucket, source_key, key_upload_dest):
        self.s3 = boto3.client("s3")
        self.bucket = bucket
        self.source_key = source_key
        self.dest_key = key_upload_dest
        self.chunk_size = 10*1024*1024 # 10 MB
        
        self.MIN_PART_SIZE = 5 * 1024 * 1024  # AWS requires that min uploads is 5 MB, when using Multi-part uploads
        self.READ_STDOUT_SIZE = 50 * 1024 * 1024  # 5MB chunks from ffmpeg
        self.max_chunk = 2 * self.chunk_size
        self.parts = []
        self.part_number = 1
        self.part_buffer = b""
        
        self.mpu = None
        self.ffmpeg = None
        self.output_queue = queue.Queue(maxsize=30)


    def _write_to_ffmpeg(self):
        start = 0
        while True:
            range_header = f"bytes={start}-{start + self.chunk_size - 1}"
            try:
                resp = self.s3.get_object(Bucket=self.bucket, Key=self.source_key, Range=range_header)
                raw_bytes = resp["Body"].read()
                if not raw_bytes:
                    break
                self.ffmpeg.stdin.write(raw_bytes)
                self.ffmpeg.stdin.flush()
                start += self.chunk_size
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'InvalidRange':
                    break
                raise
        self.ffmpeg.stdin.close()
    
    def _read_from_ffmpeg(self):
        while True:
            chunk = self.ffmpeg.stdout.read(self.READ_STDOUT_SIZE)
            if not chunk:
                break
            self.output_queue.put(chunk)
        self.output_queue.put(None)  # Sentinel
    
    def upload_some_parts(self):
        if not self.part_buffer:
            return
            
        print(f'Uploading part {self.part_number}, size={len(self.part_buffer)} bytes')
        part_resp = self.s3.upload_part(
            Bucket=self.bucket,
            Key=self.dest_key,
            PartNumber=self.part_number,
            UploadId=self.mpu["UploadId"],
            Body=self.part_buffer
        )
        self.parts.append({
            "ETag": part_resp["ETag"], 
            "PartNumber": self.part_number
        })
        self.part_number += 1
    
    def _process_output_queue(self):
        shitty_chunk_count = 0
        while True:
            chunk_ff_out = self.output_queue.get()
            
            if chunk_ff_out is None:  # Done
                self.upload_some_parts()
                break
            
            if shitty_chunk_count % 200 == 0:
                print(f"Chunk {shitty_chunk_count}: read {len(chunk_ff_out)} bytes, part_buffer: {len(self.part_buffer)} bytes")
                
            ### 💣 BOOM ###
            self.part_buffer += chunk_ff_out
            
            if len(self.part_buffer) >= self.MIN_PART_SIZE:
                self.upload_some_parts()
                self.part_buffer = b""
            
            shitty_chunk_count += 1
    
    def _complete_upload(self):
        if not self.parts:
            print("File too small for multipart, using regular upload")
            self.s3.abort_multipart_upload(
                Bucket=self.bucket,
                Key=self.dest_key,
                UploadId=self.mpu["UploadId"]
            )
            self.s3.put_object(
                Bucket=self.bucket,
                Key=self.dest_key,
                Body=self.part_buffer
            )
        else:
            self.s3.complete_multipart_upload(
                Bucket=self.bucket,
                Key=self.dest_key,
                UploadId=self.mpu["UploadId"],
                MultipartUpload={"Parts": self.parts}
            )
            print(f"Upload complete: {len(self.parts)} parts")
    
    def transcode(self):
        print(f"Starting transcode: {self.source_key} -> {self.dest_key}")
        
        # Initialize multipart upload
        self.mpu = self.s3.create_multipart_upload(
            Bucket=self.bucket, 
            Key=self.dest_key
        )
        
        # Start ffmpeg process
        self.ffmpeg = subprocess.Popen(
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
                '-f', 'opus',
                '-vn',  # No video
                'pipe:1'  # Output to stdout
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )
        
        # Start worker threads
        write_thread = threading.Thread(target=self._write_to_ffmpeg)
        read_thread = threading.Thread(target=self._read_from_ffmpeg)
        
        write_thread.start()
        read_thread.start()
        
        # Process output and upload
        self._process_output_queue()
        
        # Wait for threads to complete
        write_thread.join()
        read_thread.join()
        
        # Wait for ffmpeg to finish
        self.ffmpeg.wait()
        
        # Complete the upload
        self._complete_upload()
        
        print(f"Transcode complete: @ {self.dest_key}")
        return 


# Example usage
if __name__ == "__main__" and not "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
    bucket    = "my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket"
    key_small = "channels/vod-audio/caedrel/2510842357/BUDAPEST_MAJOR_-_FAZE_ELIMINATION-v2629297105.mp4"
    key_big   = "channels/vod-audio/caedrel/2510842357/DROPS_NUT_RAIDERS_TESTICULAR_TORSION_TUESDAY_EXPEDITION_TIME_BUNGULATE-v2628130294.mp4"

    key            = key_big
    dest_key     = key.replace(".mp4", "_420_CLAUDE_MAGIC_XXX.opus")

    transcoder = Ffmpeg_Mp4_to_Opus(bucket, key)
    dest_key = transcoder.transcode()