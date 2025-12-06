import time
import boto3
import subprocess
import io
from botocore.exceptions import ClientError

class S3StreamProcessor:
    def __init__(self, bucket_name, chunk_size=10*1024*1024):  # 10MB chunks

        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name
        self.chunk_size = chunk_size
    
    def process_and_upload(self, source_key, dest_key):

        # Get file size
        response = self.s3_client.head_object(Bucket=self.bucket_name, Key=source_key)
        file_size = response['ContentLength']
        
        print(f"Starting processing: {source_key} ({file_size / (1024*1024):.2f} MB)")
        print(f"Chunk size: {self.chunk_size / (1024*1024):.2f} MB")
        print(f"Estimated chunks: {(file_size + self.chunk_size - 1) // self.chunk_size}")

        # Initialize multipart upload
        multipart = self.s3_client.create_multipart_upload(
            Bucket=self.bucket_name,
            Key=dest_key,
            ContentType='audio/opus'  # ← Add it here!
        )
        upload_id = multipart['UploadId']
        
        parts = []
        part_number = 1
        ffmpeg_error = None
        
        
        try:
            # Start ffmpeg process
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
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
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # bufsize=self.chunk_size
                bufsize=0  # 0 = Send immediately. (prevents deadlock)
            )
            
            # Stream input to ffmpeg in a separate thread
            import threading

            def feed_ffmpeg():
                nonlocal ffmpeg_error
                try:
                    byte_range_start = 0
                    chunk_num_debug = 0
                    while byte_range_start < file_size:
                        byte_range_end = min(byte_range_start + self.chunk_size, file_size) - 1
                        
                        response = self.s3_client.get_object(
                            Bucket=self.bucket_name,
                            Key=source_key,
                            Range=f'bytes={byte_range_start}-{byte_range_end}'
                        )
                        
                        chunk_num_debug += 1
                        progress = (byte_range_end + 1) / file_size * 100
                        chunk = response['Body'].read()
                        process.stdin.write(chunk)
                        process.stdin.flush()  # ← ADD THIS! Forces data to ffmpeg immediately
                        
                        print(f"  Input: Downloaded chunk {chunk_num_debug} ({progress:.1f}% of input)")
                        byte_range_start += self.chunk_size  # ← Much clearer!
                    
                    process.stdin.close()
                    print("  Input: Finished feeding ffmpeg")
                except Exception as e:
                    ffmpeg_error = e
                    print(f"  Input error: {e}")
                    try:
                        process.stdin.close()
                    except:
                        pass
                
            # Read output from ffmpeg and upload
            def read_and_upload():
                nonlocal ffmpeg_error, part_number, parts
                try:
                    output_buffer = io.BytesIO()
                    
                    while True:
                        processed_chunk = process.stdout.read(self.chunk_size)
                        if not processed_chunk:
                            break
                        
                        output_buffer.write(processed_chunk)
                        
                        # Upload when buffer reaches chunk size
                        if output_buffer.tell() >= self.chunk_size:
                            output_buffer.seek(0)
                            
                            response = self.s3_client.upload_part(
                                Bucket=self.bucket_name,
                                Key=dest_key,
                                PartNumber=part_number,
                                UploadId=upload_id,
                                Body=output_buffer.read()
                            )
                            
                            parts.append({
                                'PartNumber': part_number,
                                'ETag': response['ETag']
                            })
                            
                            print(f"  Output: Uploaded part {part_number}")
                            part_number += 1
                            output_buffer = io.BytesIO()
                    
                    # Upload any remaining data
                    if output_buffer.tell() > 0:
                        output_buffer.seek(0)
                        
                        response = self.s3_client.upload_part(
                            Bucket=self.bucket_name,
                            Key=dest_key,
                            PartNumber=part_number,
                            UploadId=upload_id,
                            Body=output_buffer.read()
                        )
                        
                        parts.append({
                            'PartNumber': part_number,
                            'ETag': response['ETag']
                        })
                        print(f"  Output: Uploaded final part {part_number}")
                    
                    print("  Output: Finished reading from ffmpeg")
                except Exception as e:
                    ffmpeg_error = e
                    print(f"  Output error: {e}")
            
            # Start both threads
            feed_thread = threading.Thread(target=feed_ffmpeg)
            upload_thread = threading.Thread(target=read_and_upload)
            
            feed_thread.start()
            upload_thread.start()
            
            # Wait for both to complete
            feed_thread.join()
            upload_thread.join()
            
            # Wait for ffmpeg to finish
            process.wait()
            
            if ffmpeg_error:
                raise ffmpeg_error
            
            if process.returncode != 0:
                stderr = process.stderr.read().decode()
                raise Exception(f"FFmpeg error: {stderr}")
            
            # Complete multipart upload
            self.s3_client.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=dest_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            
            print(f"Successfully processed and uploaded {dest_key}")
            
        except Exception as e:
            # Abort multipart upload on error
            self.s3_client.abort_multipart_upload(
                Bucket=self.bucket_name,
                Key=dest_key,
                UploadId=upload_id
            )
            raise e


# Example usage
if __name__ == '__main__':
    start_time = time.time()
    processor = S3StreamProcessor(
        bucket_name="my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket",
        chunk_size=10*1024*1024  # 10MB chunks
    )
    key_small = "channels/vod-audio/caedrel/2510842357/BUDAPEST_MAJOR_-_FAZE_ELIMINATION-v2629297105.mp4"
    key_big   = "channels/vod-audio/caedrel/2510842357/DROPS_NUT_RAIDERS_TESTICULAR_TORSION_TUESDAY_EXPEDITION_TIME_BUNGULATE-v2628130294.mp4"
    # Example: Convert video to H.264 with reduced quality
    dest = key_big.replace(".mp4", "_small_MAGIC.opus")
    processor.process_and_upload(
        source_key=key_big,
        dest_key=dest,
    )
    runtime_secs = time.time() - start_time    
    print("\n    (zzzzzzzzzzzzz): run time (secs) = " + str(int(runtime_secs)) + "\n")