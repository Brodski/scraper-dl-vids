import json
from typing import Dict, Any

class ScrappedChannel:
    displayname = str
    language = str
    links = list[str]
    logo = str
    rownum = int
    twitchurl = str
    url = str

    def __init__(self, **kwargs):        
        self.displayname = kwargs.get('displayname')
        self.language = kwargs.get('language')
        self.links = kwargs.get('links')
        self.logo = kwargs.get('logo')
        self.rownum = kwargs.get('rownum')
        self.twitchurl = kwargs.get('twitchurl')
        self.url = kwargs.get('url')