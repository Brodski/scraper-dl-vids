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

    def __init__(self, id="", channels_name_id="", transcript_status="", priority="", channel_current_rank="", todo_date=""):
        self.id = id
        self.channels_name_id = channels_name_id
        self.transcript_status = transcript_status
        self.priority = priority
        self.channel_current_rank = channel_current_rank
        self.todo_date = todo_date

    def print(self):
        max_attr_length = max(len(attr) for attr in dir(self) if not attr.startswith('__') and not callable(getattr(self, attr)))
        print(self)
        for attr in dir(self):
            # filter out special methods and attributes
            if not attr.startswith('__') and not callable(getattr(self, attr)):
                # print(f"    {attr}: {getattr(self, attr)}")
                value = getattr(self, attr)
                print(f"{attr.ljust(max_attr_length)} | {value}")

