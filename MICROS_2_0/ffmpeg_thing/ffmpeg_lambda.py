import re
import subprocess
import traceback
import boto3 # boto3 comes for free in all lambda :o
import os
import time
# import pymysql


os.environ["LD_LIBRARY_PATH"] = "/opt/lib:" + os.environ.get("LD_LIBRARY_PATH", "")


s3 = boto3.client("s3")


def lambda_handler(event, context):
    print(event)
    print("------------")
    print("------------")
    print("------------")
    print(event['Records'])
    # for-loop b/c "when multiple files are uploaded very quickly (within milliseconds), AWS might batch them into a single Lambda invocation for efficiency"
    for record in event['Records']:
        print("going ....")
        bucket          = record['s3']['bucket']['name']
        key             = record["s3"]["object"]["key"]
        event_name      = record['eventName']
        object_size     = record['s3']['object']['size']
        key_upload_dest = key.replace(".mp4", ".opus")
        
        if key.endswith('/'): # b/c folder 
            print(f"Skipping folder: {key}")
            continue

        if event_name.startswith('ObjectCreated'):
            _execSubprocCmd(["ffmpeg", "--version"])
            print("@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@")
            print(f"Processing {event_name} for {key} in {bucket}")
            print(f"File size: {object_size} bytes")
            # _execSubprocCmd(["/opt/bin/ffmpeg", "--version"])

            
            download_path = f"/tmp/{os.path.basename(key)}"
            s3.download_file(bucket, key, download_path)
            outFile_local, runtime_secs = convertVideoToSmallAudio(download_path)
            # output_key = f"testz/{os.path.basename(key)}"
            
            print("outFile_local")
            print(outFile_local)
            print("key_upload_dest")
            print(key_upload_dest)
            if key_upload_dest.endswith(".mp4"):
                raise Exception("Ah hell no!! Wrong file format, failed to convert")
            return "gg"
            s3.upload_file(outFile_local, bucket, key_upload_dest, ExtraArgs={ 'ContentType': 'audio/mpeg'})
            updateVods_Db(outFile_local)

        elif event_name.startswith('ObjectRemoved'):
            print(f"File {key} was deleted from {bucket}")


    time.sleep(100)
    return {
        "statusCode": 200,
        "body": f"Processed and uploaded to {key_upload_dest}"
    }


def convertVideoToSmallAudio(download_path):
    print("*************************************************")
    print("*******    convertVideoToSmallAudio     *********")
    print("*************************************************")
    start_time = time.time()

    last_dot_index = download_path.rfind('.')
    inFile = "file:" + download_path[:last_dot_index] + ".mp4" 
    outFile = "file:" + download_path[:last_dot_index] + ".opus" #opus b/c of the ffmpeg cmd below
    outFile_local = download_path[:last_dot_index] + ".opus"

    # https://superuser.com/questions/1422460/codec-and-setting-for-lowest-bitrate-ffmpeg-output
    ffmpeg_command = [ 'ffmpeg', '-y', '-i',  inFile, '-c:a', 'libopus', '-ac', '1', '-ar', '16000', '-b:a', '10K', '-vbr', 'constrained', '-application', 'voip', '-compression_level', '5', outFile ]
    
    print("    (convertVideoToSmallAudio): compressing Audio....\n")
    _execSubprocCmd(ffmpeg_command)

    runtime_secs = time.time() - start_time    
    print("\n    (convertVideoToSmallAudio): run time (secs) = " + str(int(runtime_secs)) + "\n")
    return outFile_local, runtime_secs




def _execSubprocCmd(ffmpeg_command):
    print("ffmpeg_command")
    print(ffmpeg_command)
    
    try:
        process = subprocess.run(
            ffmpeg_command,
            text=True,              # get output as str instead of bytes
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            # check=True
        )
        stdoutput = process.stdout
        stderr = process.stderr
        returncode = process.returncode
        # print("stdoutput: ", stdoutput)
        # print("stderr: ", stderr)
        print("returncode: ", returncode)        
        return stdoutput, stderr
    except subprocess.CalledProcessError as e:
        print("Failed to run ffmpeg command:")
        print(e)
        traceback.print_exc()
        # raise
        return False
    

def updateVods_Db(key):
    # key = "BUDAPEST_MAJOR_-_FAZE_ELIMINATION-v2629297105.opus"
    match = re.search(r'v(\d+)\.opus$', key)
    vod_id = None
    extension = None
    transcript_status = "audio2text_need"
    if match:
        vod_id = match.group(1)
        print("vod_id", vod_id)
        print("extension", extension)
    if vod_id == None:
        raise Exception("AUDIO NEEDS TO BE OPUS")

    connection = getConnection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE Vods
                SET TranscriptStatus = %s,
                    DownloadDate = NOW()
                WHERE Id = %s;
                """
            values = (transcript_status, vod_id)
            affected_count = cursor.execute(sql, values)
            print("    (updateVods_Db) Updated " + vod_id + ". affected_counf= " + str(affected_count))
            print("    (updateVods_Db) Updated " + vod_id + ". affected_counf= " + str(affected_count))
            connection.commit()
            return True
    except Exception as e:
        print(f"    (updateVods_Db) Error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()




def getConnection():
    DATABASE = os.getenv("DATABASE")
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_PORT = os.getenv("DATABASE_PORT")
    # connection = MySQLdb.connect(
    connection = pymysql.connect(
        db      = DATABASE,
        host    = DATABASE_HOST,
        user    = DATABASE_USERNAME,
        passwd  = DATABASE_PASSWORD,
        port    = int(DATABASE_PORT),
        autocommit  = False,
    )
    return connection


EVENT_S3_MOCK = {
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "2025-12-03T12:37:51.823Z",
      "eventName": "ObjectCreated:CompleteMultipartUpload",
      "userIdentity": {
        "principalId": "A3HV734S6HGGTB"
      },
      "requestParameters": {
        "sourceIPAddress": "73.153.73.181"
      },
      "responseElements": {
        "x-amz-request-id": "DK3KRJW07T6Y8RN9",
        "x-amz-id-2": "lsQ1/BmBs3+FfPoXSpbbsbQzBr4TWox5cQQfIFXCMzpdR2Oc9n/+GkovTebpcIDbXL1eBhc52ZJpFRReNSxQJ/5PnEKEbg9J"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "upload_ffmpeg_event",
        "bucket": {
          "name": "my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket",
          "ownerIdentity": {
            "principalId": "A3HV734S6HGGTB"
          },
          "arn": "arn:aws:s3:::my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket"
        },
        "object": {
          "key": "channels/vod-audio/caedrel/2510842357/DROPS_NUT_RAIDERS_TESTICULAR_TORSION_TUESDAY_EXPEDITION_TIME_BUNGULATE-v2628130294.mp4",
          "size": 2372983146,
          "eTag": "b42352666a2d651202c4af8371714f3a-139",
          "sequencer": "0069302D3C7960E32B"
        }
      }
    }
  ]
}

import sys
if __name__ == "__main__" and not "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
    # lambda_handler(EVENT_S3_MOCK, None)
    # print("DONE GG!\n" * 9)
    # time.sleep(200)
    # sys.exit(1)
    import boto3
    import subprocess
    start_time = time.time()
    bucket    = "my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket"
    key_small = "channels/vod-audio/caedrel/2510842357/BUDAPEST_MAJOR_-_FAZE_ELIMINATION-v2629297105.mp4"
    key_big   = "channels/vod-audio/caedrel/2510842357/DROPS_NUT_RAIDERS_TESTICULAR_TORSION_TUESDAY_EXPEDITION_TIME_BUNGULATE-v2628130294.mp4"
    CHUNK_SIZE = 50 * 1024 * 1024  # 50 MB chunks
    s3        = boto3.client("s3")
    resp      = s3.get_object(Bucket=bucket, Key=key_big)
    body      = resp["Body"]

    outFile = "audio.opus"
    
    mpu = s3.create_multipart_upload(Bucket=bucket, Key=key_small)
    parts = []

    ffmpeg_command = [
        'ffmpeg', 
        '-y', 
        '-i', 'pipe:0',
        '-c:a', 'libopus', 
        '-ac', '1', 
        '-ar', '16000',
        '-b:a', '10K', 
        '-vbr', 'constrained',
        '-application', 'voip', 
        '-compression_level', '5',
        outFile
    ]

    proc = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
    for chunk in iter(lambda: body.read(64*1024), b''):
        proc.stdin.write(chunk)

    runtime_secs = time.time() - start_time    
    print("\n    (zzzzzzzzzzzzz): run time (secs) = " + str(int(runtime_secs)) + "\n")
    proc.stdin.close()
    proc.wait()


