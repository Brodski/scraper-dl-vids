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

    RETENTION_IN_DAYZ = 30
    LOG_GROUP_NAME = '/vastai/transcriber/' + env_varz.ENV
    LOG_STREAM_NAME = f'{env_varz.ENV}_{datetime.datetime.utcnow().strftime("%Y_%m_%d-%H.%M.%S")}' if env_varz.ENV != "local" else "local"

    # Create Log Group
    try:
        res = cw_client.create_log_group(logGroupName=LOG_GROUP_NAME)
        print('res', res)
    except cw_client.exceptions.ResourceAlreadyExistsException as e:
        print('\nLog group already exists:', LOG_GROUP_NAME)
    except Exception as e:
        print(f"Cloudwatch error 1: {e}")

    # Create Log Stream
    try:
        res2 = cw_client.create_log_stream(logGroupName=LOG_GROUP_NAME, logStreamName=LOG_STREAM_NAME)
        print('res2', res2)
    except cw_client.exceptions.ResourceAlreadyExistsException as e:
        print('\nLog stream already exists:', LOG_STREAM_NAME)
    except Exception as e:
        print(f"Cloudwatch error 2: {e}")

    # Create retention policy
    try:
        res3 = cw_client.put_retention_policy(
            logGroupName=LOG_GROUP_NAME,
            retentionInDays=RETENTION_IN_DAYZ
        ) 
        time.sleep(1)
    except Exception as e:
        print(f"Cloudwatch error 3: {e}")

    @classmethod
    def log(cls, *args):
        # print("---------------------------------------------")
        # print(cls.cw_client, f"{cls.LOG_GROUP_NAME} --- {cls.LOG_STREAM_NAME}")
        if not args:
            print()
            return

        try:
            msg = " ".join(str(arg) for arg in args)
        except Exception as error:
            print(f"Failed it: {error}")
            print(args)
        print(msg)

        if env_varz.WHSP_IS_CLOUDWATCH == "True":
            try:
                log_res = cls.cw_client.put_log_events(
                    logGroupName=cls.LOG_GROUP_NAME,
                    logStreamName=cls.LOG_STREAM_NAME,
                    logEvents=[
                        {
                            'timestamp': int(time.time() * 1000),  # Current time in milliseconds
                            'message': msg
                        }
                    ]
                )
            except Exception as error:
                print(f"Failed to send log event to CloudWatch: {error}")
