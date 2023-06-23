import json
from typing import Dict, Any

class AudioResponse:
    channel = str
    vod_ids = list[int]
    vod_titles = list[str]

    def __init__(self, **kwargs):
        self.channel = kwargs.get('channel')
        self.vod_ids = kwargs.get('vod_ids')
        self.vod_titles = kwargs.get('vod_titles')
        # self.vod_titles = kwargs.get('vod_titles')

    
