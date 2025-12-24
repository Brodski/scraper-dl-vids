import datetime
import os
import boto3
import logging
import time
# import env_file as env_varz
from env_file import env_varz
from botocore.exceptions import ClientError

# https://stackoverflow.com/questions/30897897/python-boto-writing-to-aws-cloudwatch-logs-without-sequence-token
# boto3 docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html
class Cloudwatch(logging.Handler):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # prevent re-initialization
        if hasattr(self, "_initialized") and self._initialized:
            return


    def __init__(self):
        super().__init__()
        self.cw_client = boto3.client('logs', region_name='us-east-1')
        
        self.LOG_GROUP_NAME = '/scraper/transcriber/' + env_varz.ENV
        self.LOG_STREAM_NAME = f'{env_varz.ENV}_{os.getenv("CONTAINER_ID")}_count{os.getenv("TRANSCRIBER_INSTANCE_CNT")}_{datetime.datetime.utcnow().strftime("%Y_%b_%d-%Hh_%M")}' if env_varz.ENV != "local" else "local"
        # prod_12345_count2_@2024_Sep_06-22h_27m

        RETENTION_IN_DAYZ = 30

        # Create Log Group ... "prod_12345_2_@2024_Sep_06-22h_27m"
        try:
            res = self.cw_client.create_log_group(logGroupName=self.LOG_GROUP_NAME)
            print('res', res)
        except self.cw_client.exceptions.ResourceAlreadyExistsException as e:
            print('\nLog group already exists:', self.LOG_GROUP_NAME)
        except Exception as e:
            print(f"Cloudwatch error 1: {e}")

        # Create Log Stream
        try:
            res2 = self.cw_client.create_log_stream(logGroupName=self.LOG_GROUP_NAME, logStreamName=self.LOG_STREAM_NAME)
            # print('res2', res2)
        except self.cw_client.exceptions.ResourceAlreadyExistsException as e:
            print('\nLog stream already exists:', self.LOG_STREAM_NAME)
        except Exception as e:
            print(f"Cloudwatch error 2: {e}")

        # Create retention policy
        try:
            res3 = self.cw_client.put_retention_policy(
                logGroupName=self.LOG_GROUP_NAME,
                retentionInDays=RETENTION_IN_DAYZ
            ) 
            time.sleep(1)
        except Exception as e:
            print(f"Cloudwatch error 3: {e}")

    # "logging" expects `emit()` for each handler
    def emit(self, record):
        msg = self.format(record)
        # msg = self.log(record)
        try:
            log_res = self.cw_client.put_log_events(
                logGroupName=self.LOG_GROUP_NAME,
                logStreamName=self.LOG_STREAM_NAME,
                logEvents=[
                    {
                        'timestamp': int(time.time() * 1000),  # Current time in milliseconds
                        'message': msg
                    }
                ]
            )
        except Exception as error:
            print(f"Failed to send log event to CloudWatch: {error}")

    def log(self, *args):
        if not args:
            # print()
            return ""

        msg = " ".join(str(arg) for arg in args)
        msg = self.format(msg)
        return msg
        

        # print(msg) <----- old way (before 'python logging')

        # if env_varz.WHSP_IS_CLOUDWATCH == "True":
        #     try:
        #         log_res = self.cw_client.put_log_events(
        #             logGroupName=self.LOG_GROUP_NAME,
        #             logStreamName=self.LOG_STREAM_NAME,
        #             logEvents=[
        #                 {
        #                     'timestamp': int(time.time() * 1000),  # Current time in milliseconds
        #                     'message': msg
        #                 }
        #             ]
        #         )
        #     except Exception as error:
        #         print(f"Failed to send log event to CloudWatch: {error}")
