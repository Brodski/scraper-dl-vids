import json
import urllib
import env_file as env_varz
from typing import Dict, Any

class Vod:
    id = str
    channels_name_id = str
    transcript_status = str
    priority = int 
    channel_current_rank = str # optional

    def __init__(self, id="", channels_name_id="", transcript_status="", priority="", channel_current_rank="" ):
        self.id = id
        self.channels_name_id = channels_name_id
        self.transcript_status = transcript_status
        self.priority = priority
        self.channel_current_rank = channel_current_rank

