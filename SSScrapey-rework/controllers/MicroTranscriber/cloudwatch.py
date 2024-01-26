import datetime
import boto3
import logging
import time
import env_file as env_varz
from botocore.exceptions import ClientError

# https://stackoverflow.com/questions/30897897/python-boto-writing-to-aws-cloudwatch-logs-without-sequence-token
# boto3 docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html
class Cloudwatch:
    cw_client = boto3.client('logs', region_name='us-east-1')
    LOG_GROUP_NAME = '/vastai/transcriber/' + env_varz.ENV
    LOG_STREAM_NAME = f'{datetime.datetime.utcnow().strftime("%Y_%m_%d-%H.%M.%S")}'
    try:
        res = cw_client.create_log_group(logGroupName=LOG_GROUP_NAME)
        print('res', res)
    except cw_client.exceptions.ResourceAlreadyExistsException as e:
        print('\nLog group already exists:', LOG_GROUP_NAME)
    except Exception as e:
        print(f"Cloudwatch error 1: {e}")


    try:
        res2 = cw_client.create_log_stream(logGroupName=LOG_GROUP_NAME, logStreamName=LOG_STREAM_NAME)
        print('res2', res2)
    except cw_client.exceptions.ResourceAlreadyExistsException as e:
        print('\nLog stream already exists:', LOG_STREAM_NAME)
    except Exception as e:
        print(f"Cloudwatch error 2: {e}")

    @classmethod
    def push_logs(cls, message):
        try:
            response = cls.cw_client.describe_log_streams(logGroupName=cls.LOG_GROUP_NAME, logStreamNamePrefix=cls.LOG_STREAM_NAME)

            if 'logStreams' in response and len(response['logStreams']) > 0:
                sequence_token = response['logStreams'][0].get('uploadSequenceToken')

            log_event = {
                'logGroupName': cls.LOG_GROUP_NAME,
                'logStreamName': cls.LOG_STREAM_NAME,
                'logEvents': [
                    {
                        'timestamp': int(round(time.time() * 1000)),  # Current time in milliseconds
                        'message': message
                    }
                ]
            }

            # If sequence token exists, add it to the request
            if 'sequenceToken' in locals():
                log_event['sequenceToken'] = sequence_token
            print("--------- putting some shit ----------")
            print(log_event)
            cls.cw_client.put_log_events(**log_event)
        except ClientError as error:
            print(f"Failed to send log event to CloudWatch: {error}")
