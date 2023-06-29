import json
from typing import Dict, Any

class Vod:
    channel = str
    id = str
    title = str
    link_s3 = str
    language = str

    def __init__(self, *, channel="", id="", title="", link_s3="", language=""):
        self.channel = channel
        self.id = id
        self.title = title
        self.link_s3 = link_s3
        # self.vod_titles = kwargs.get('vod_titles')

    
