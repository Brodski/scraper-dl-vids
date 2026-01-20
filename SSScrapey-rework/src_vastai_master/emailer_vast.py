import boto3
import os
from Configz import configz
def sendEmail(subject, body):
    env = os.getenv("ENV") or configz.ENV
    ses = boto3.client('ses', region_name='us-east-1')
    response = ses.send_email(
        Source=f'noreply@{env}-captions.bski.one', # TODO update "dev"-catpions
        # Source=f'noreply@{env_varz.ENV}-captions.bski.one', # TODO update "dev"-catpions
        Destination={
            'ToAddresses': [
                'cbrodski@gmail.com',
                # 'loganwallace.smash@gmail.com',
            ],
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': 'UTF-8'
                }
            }
        }
    )


class MetadataVast():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.deleted        = [] # {id, runtime}
        self.created        = [] # {id, runtime}
        self.try_again_arr  = [] # {id, runtime}
        self.successes      = [] # {id, runtime}
        self.errorz         = []

    def empty_singleton_bc_lambda(self):
        self.deleted        = []
        self.created        = []
        self.try_again_arr  = []
        self.successes      = []
        self.errorz         = []

    def send_fail_msg(self, trace=""):
        env = os.getenv("ENV") or configz.ENV
        subject = f"Vast-master/Lambda {env} Failed"
        body = self.format_msg()
        body = body + "\n\n\n" + trace
        print(subject)
        print(body)
        sendEmail(subject, body)
        self.empty_singleton_bc_lambda()

    def send_success_msg(self):
        env = os.getenv("ENV") or configz.ENV
        subject = f"Vast-master/Lambda {env} Success"
        body = self.format_msg()

        print(subject)
        print(body)
        sendEmail(subject, body)
        self.empty_singleton_bc_lambda()

    def format_msg(self):
        def appender(items):
            msg = ""
            for i, thing in enumerate(items):
                if i >= 1: 
                    msg += "------------------------\n"
                for key, value in thing.items():
                    # if key in ("id", "exec_time_minutes", "cpu_name", "gpu_name", "status_msg", "actual_status", "geolocation", "dph_total"):
                    if key in ("id", "exec_time_minutes", "cpu_name", "gpu_name", "actual_status", "geolocation", "dph_total"):
                        msg += f"{key}: {value}\n"
                        # msg += "\n"
            return msg
        ######################
        ### AWS CLI HELPER ###
        ######################
        awslogs_group  = os.environ.get("AWS_LAMBDA_LOG_GROUP_NAME")
        awslogs_stream = os.environ.get("AWS_LAMBDA_LOG_STREAM_NAME")
        awslogs_region = os.environ.get("AWS_REGION")
        if awslogs_group == None:
            awslogs_group = "group_localzzz"
        if awslogs_stream == None:
            awslogs_stream = "stream_localzzz"
        if awslogs_region == None:
            awslogs_region = "region_localzzz"
        filename = awslogs_stream.replace("/", ".").replace("\\", ".").replace('[$LATEST]', '_')
        out_ = f"C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids\\logs\\{filename}.txt"
        cli = "\n"
        cli = cli + "set PYTHONUTF8=1\n"
        cli = cli + "aws logs get-log-events "
        cli = cli + f" --log-group-name '{awslogs_group}' "
        cli = cli + f" --log-stream-name '{awslogs_stream}' "
        cli = cli + f" --region {awslogs_region} "
        cli = cli + f" --output text > '{out_}' \n\n"
        cli = cli + r"\s*\d+\s*\n\s*EVENT"
        #######################
        ### ACTUAL MESSAGES ###
        #######################
        msg = ""
        msg += f"Group: {awslogs_group}\n"
        msg += f"Stream: {awslogs_stream}\n"
        msg += f"Region: {awslogs_region}\n"
        msg += " ----- SUCCESSES -----\n"
        msg += appender(self.successes)

        msg += " ----- ERRORS -----\n"
        msg += appender(self.errorz)
        
        msg += " ----- TRY_AGAINS -----\n"
        msg += appender(self.try_again_arr)
        
        msg += " ----- CREATED -----\n"
        msg += appender(self.created)
        
        msg += " ----- DELETED -----\n"
        msg += appender(self.deleted)
        msg += cli

        return msg
