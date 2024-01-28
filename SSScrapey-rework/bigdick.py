import datetime
import json
import boto3
import logging
import time
import random
import string
# import env_file as env_varz
from botocore.exceptions import ClientError

# https://stackoverflow.com/questions/30897897/python-boto-writing-to-aws-cloudwatch-logs-without-sequence-token
# boto3 docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html
def generate_random_string(length):
    characters = string.ascii_letters + string.digits  # You can include more characters if needed
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


class Cloudwatch(object):
    _instance = None

    random_string = generate_random_string(10)  # Generates a random string of length 10
    print(random_string)
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Cloudwatch, cls).__new__(cls, *args, **kwargs)
            cls.nextSequenceToken = None
            cls.cw_client = None
            cls.LOG_GROUP_NAME = None
            cls.LOG_STREAM_NAME = None
            cls.__initialize(cls)
        return cls._instance
    
    def testshit(self):
        print('testing...............')
        for i in range(0,5):
            print(self.cw_client, f"{self.LOG_GROUP_NAME} --- {self.LOG_STREAM_NAME}")
            res = self.cw_client.put_log_events(
                logGroupName=self.LOG_GROUP_NAME,
                logStreamName=self.LOG_STREAM_NAME,
                logEvents=[
                        {
                            'timestamp': int(time.time() * 1000),  # Current time in milliseconds
                            'message': json.dumps(str(i))
                        }
                    ]
                )
            print()
            print(res)

    def __initialize(self): 
        # self.nextSequenceToken = None
        # self.cw_client = None
        # self.LOG_GROUP_NAME = None
        # self.LOG_STREAM_NAME = None

        self.cw_client = boto3.client('logs', region_name='us-east-1')
        self.LOG_GROUP_NAME = '/vastai/transcriber/shit'
        self.LOG_STREAM_NAME = generate_random_string(11)
        try:
            # self.LOG_STREAM_NAME = f'{datetime.datetime.utcnow().strftime("%Y_%m_%d-%H.%M.%S")}'
            # self.LOG_STREAM_NAME = "eat-my-ass"

            res = self.cw_client.create_log_group(logGroupName=self.LOG_GROUP_NAME)
            time.sleep(1)
            print('\nres', res)
        except self.cw_client.exceptions.ResourceAlreadyExistsException as e:
            print('Log group already exists:', self.LOG_GROUP_NAME, '\n')
        except Exception as e:
            print(f"Cloudwatch error 1: {e}")

        try:
            res2 = self.cw_client.create_log_stream(logGroupName=self.LOG_GROUP_NAME, logStreamName=self.LOG_STREAM_NAME)
            time.sleep(1)
            print('Log stream created :', res2), '\n'
        except self.cw_client.exceptions.ResourceAlreadyExistsException as e:
            print('Log stream already exists:', self.LOG_STREAM_NAME), '\n'
        except Exception as e:
            print(f"Cloudwatch error 2: {e}")

        try:
            res3 = self.cw_client.put_retention_policy(
                logGroupName=self.LOG_GROUP_NAME,
                retentionInDays=30 # 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365 ...  more
            ) 
            time.sleep(1)
        except Exception as e:
            print(f"Cloudwatch error 3: {e}")

    def log(self, *args):
        print("---------------------------------------------")
        print(self.cw_client, f"{self.LOG_GROUP_NAME} --- {self.LOG_STREAM_NAME}")
        msg = ""
        for arg in args:
            msg = f"{msg} {str(arg)}"
        print(msg)

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
            print(msg)
            print(args)
            print()




if __name__ == "__main__":
    cw = Cloudwatch()
    cw.testshit()