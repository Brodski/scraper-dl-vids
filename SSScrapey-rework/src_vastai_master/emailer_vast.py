import boto3
import os

def sendEmail(subject, body):
    ses = boto3.client('ses', region_name='us-east-1')
    response = ses.send_email(
        Source='noreply@dev-captions.bski.one', # TODO update "dev"-catpions
        Destination={
            'ToAddresses': [
                'loganwallace.smash@gmail.com',
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

    def send_fail_msg(self, trace=""):
        env = os.getenv("ENV")
        subject = f"Vast-master/Lambda {env} Failed"
        body = self.format_msg()
        body = body + "\n\n\n" + trace
        print(subject)
        print(body)
        sendEmail(subject, body)

    def send_success_msg(self):
        env = os.getenv("ENV")
        subject = f"Vast-master/Lambda {env} Success"
        body = self.format_msg()

        print(subject)
        print(body)
        sendEmail(subject, body)

    def format_msg(self):
        def appender(items):
            msg = ""
            for err in items:
                for key, value in err.items():
                    msg += f"{key}: {value}\n"
            return msg

        msg = ""
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

        return msg
