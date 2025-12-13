import re
import traceback
import os
import time
import sys
import subprocess
from Ffmpeg_Mp4_to_Opus import Ffmpeg_Mp4_to_Opus
import pymysql


os.environ["LD_LIBRARY_PATH"] = "/opt/lib:" + os.environ.get("LD_LIBRARY_PATH", "") # do this to make ffmpeg work in our subcommand (lambda layer)


def lambda_handler(event, context):
    print(event)
    print("------------")
    print("------------")
    print("------------")
    # for-loop b/c "when multiple files are uploaded very quickly (within milliseconds), AWS might batch them into a single Lambda invocation for efficiency"
    for record in event['Records']:
        print("going ....")
        bucket          = record['s3']['bucket']['name']
        key             = record["s3"]["object"]["key"]
        event_name      = record['eventName']
        object_size     = record['s3']['object']['size']
        key_upload_dest = key.replace(".mp4", "_NIKKI_dec7_v123.opus")
        print("--> bucket:           ", bucket)        
        print("--> key:              ", key)
        print("--> event_name:       ", event_name)    
        print("--> object_size:      ", object_size)        
        print("--> key_upload_dest:  ", key_upload_dest)            


        if key.endswith('/'): # b/c folder 
            print(f"Skipping folder: {key}")
            continue

        if event_name.startswith('ObjectCreated'):
            print("@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@")
            print("@@@@@@@@@@@@@@@@@@@@@@@@")
            print(f"Processing {event_name} for {key} in {bucket}")
            print(f"File size: {object_size} bytes")
            # _execSubprocCmd(["/opt/bin/ffmpeg", "--version"])

            print("begin compression..........")
            print("begin compression..........")
            print("begin compression..........")
            print("key_upload_dest")
            print(key_upload_dest)
            start = time.time()
            
            ffmpeg_mp4_to_opus: Ffmpeg_Mp4_to_Opus = Ffmpeg_Mp4_to_Opus(bucket, key, key_upload_dest)
            ffmpeg_mp4_to_opus.transcode()
            runtime = time.time() - start
            runtime = int(runtime)
            runtime_min = runtime / 60
            print(f"RUNTIME TOTAL = {runtime} = {runtime_min} min")
            print(f"RUNTIME TOTAL = {runtime} = {runtime_min} min")
            print(f"RUNTIME TOTAL = {runtime} = {runtime_min} min")
            print(f"RUNTIME TOTAL = {runtime} = {runtime_min} min")
            print(f"RUNTIME TOTAL = {runtime} = {runtime_min} min")
            updateVods_Db(key_upload_dest)

            print("GG END ")
            print("GG END ")
            print("GG END ")
        elif event_name.startswith('ObjectRemoved'):
            print(f"File {key} was deleted from {bucket}")


    time.sleep(100)
    return {
        "statusCode": 200,
        "body": f"Processed and uploaded to {key_upload_dest}"
    }
















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

if __name__ == "__main__" and not "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
    import boto3 # boto3 comes for free in all lambda :o
    bucket    = "my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket"
    key_small = "channels/vod-audio/caedrel/2510842357/BUDAPEST_MAJOR_-_FAZE_ELIMINATION-v2629297105.mp4"
    key_big   = "channels/vod-audio/caedrel/2510842357/DROPS_NUT_RAIDERS_TESTICULAR_TORSION_TUESDAY_EXPEDITION_TIME_BUNGULATE-v2628130294.mp4"
    lambda_handler(EVENT_S3_MOCK, None)

    # s3 = boto3.client("s3")
    # key            = key_big
    # output_key     = key.replace(".mp4", "_420_CLAUDE_MAGIC_XXX.opus")

    # ffmpeg_mp4_to_opus: Ffmpeg_Mp4_to_Opus = Ffmpeg_Mp4_to_Opus(bucket, key)
    # output_key = ffmpeg_mp4_to_opus.transcode()

