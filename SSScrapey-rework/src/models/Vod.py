import json
import urllib
# import env_file as env_varz
from env_file import env_varz
from typing import Dict, Any
from datetime import datetime

class Vod:
    channel_current_rank = str # optional
    channels_name_id = str
    download_date = str
    duration = int
    duration_string = str
    id = str
    language = str
    model = str
    priority = int 
    s3_audio = str
    s3_caption_files = str
    s3_thumbnails = str
    stream_date = str
    title = str
    todo_date = datetime
    transcribe_date = datetime
    transcript_status = str
    upload_date = datetime

    def __init__(self,  **kwargs):
        self.channel_current_rank = kwargs.get('channel_current_rank')
        self.channels_name_id = kwargs.get('channels_name_id')
        self.download_date = kwargs.get('download_date')
        self.duration = kwargs.get('duration')
        self.duration_string = kwargs.get('duration_string')
        self.id = kwargs.get('id')
        self.language = kwargs.get('language')
        self.model = kwargs.get('model')
        self.priority = kwargs.get('priority')
        self.s3_audio = kwargs.get('s3_audio')
        self.s3_caption_files = kwargs.get('s3_caption_files')
        self.s3_thumbnails = kwargs.get('s3_thumbnails')
        self.stream_date = kwargs.get('stream_date')
        self.title = kwargs.get('title')
        self.todo_date = kwargs.get('todo_date')
        self.transcribe_date = kwargs.get('transcribe_date')
        self.transcript_status = kwargs.get('transcript_status')
        self.upload_date = kwargs.get('upload_date')


    # def __repr__(self):
    # def __str__(self):

    def print(self):
        msg = f"VOD - {self.channels_name_id} {self.id} - {self.title} - Status: {self.transcript_status}"
        return msg

    def printDebug(self):
        max_attr_length = max(len(attr) for attr in dir(self) if not attr.startswith('__') and not callable(getattr(self, attr)))
        print(self.channels_name_id + ": " + self.__repr__() )
        for attr in dir(self):
            # filter out special methods and attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)):
                value = getattr(self, attr)
                print(f"    {attr.ljust(max_attr_length)} | {value}")

