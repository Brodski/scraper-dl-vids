import json
import urllib
import env_file as env_varz
from typing import Dict, Any
from datetime import datetime

class Vod:
    id = str
    channels_name_id = str
    transcript_status = str
    priority = int 
    channel_current_rank = str # optional
    todo_date = datetime
    upload_date = datetime
    s3_audio = str
    language = str

    def __init__(self,  **kwargs):
        self.id = kwargs.get('id')
        self.channels_name_id = kwargs.get('channels_name_id')
        self.transcript_status = kwargs.get('transcript_status')
        self.priority = kwargs.get('priority')
        self.channel_current_rank = kwargs.get('channel_current_rank')
        self.todo_date = kwargs.get('todo_date')
        self.upload_date = kwargs.get('upload_date')
        self.s3_audio = kwargs.get('s3_audio')
        self.language = kwargs.get('language')

    # TODO def __repr__(self):
    #      def __str__(self):
    def print(self):
        max_attr_length = max(len(attr) for attr in dir(self) if not attr.startswith('__') and not callable(getattr(self, attr)))
        print(self)
        for attr in dir(self):
            # filter out special methods and attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)):
                # print(f"    {attr}: {getattr(self, attr)}")
                value = getattr(self, attr)
                print(f"    {attr.ljust(max_attr_length)} | {value}")
