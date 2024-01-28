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


cw_client = boto3.client('logs', region_name='us-east-1')
LOG_GROUP_NAME = '/vastai/transcriber/shit'
LOG_STREAM_NAME = generate_random_string(11)

try:
    res = cw_client.create_log_group(logGroupName=LOG_GROUP_NAME)
    time.sleep(1)
    print('\nres', res)
except cw_client.exceptions.ResourceAlreadyExistsException as e:
    print('Log group already exists:', LOG_GROUP_NAME, '\n')
except Exception as e:
    print(f"Cloudwatch error 1: {e}")

try:
    res2 = cw_client.create_log_stream(logGroupName=LOG_GROUP_NAME, logStreamName=LOG_STREAM_NAME)
    time.sleep(1)
    print('Log stream created :', res2, '\n')
except cw_client.exceptions.ResourceAlreadyExistsException as e:
    print('Log stream already exists:', LOG_STREAM_NAME, '\n')
except Exception as e:
    print(f"Cloudwatch error 2: {e}")


def testshit():
    print('testing...............')
    for i in range(0,5):
        print(cw_client, f"{LOG_GROUP_NAME} --- {LOG_STREAM_NAME}")
        msg = json.dumps(str(i))
        print (msg)
        res = cw_client.put_log_events(
            logGroupName=LOG_GROUP_NAME,
            logStreamName=LOG_STREAM_NAME,
            # logStreamName=LOG_STREAM_NAME,
            logEvents=[
                    {
                        'timestamp': int(time.time() * 1000),
                        'message': msg
                    }
                ]
            )
        print()
        print(res)
        x = time.sleep(4)
        print(x)

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
    testshit()