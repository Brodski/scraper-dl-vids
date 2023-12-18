import json
from typing import Dict, Any

class ScrappedChannel:
    displayname = str   # "Nmplol"
    language = str      # "English"
    links = list[str]   #"https://static-cdn.jtvnw.net/jtv_user_pictures/e4d9bf96-311d-487a-b5eb-9f9a94e0f795-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
    logo = str          # ["/videos/40792901", "/videos/1470165627"],
    current_rank = int  # 22
    twitchurl = str     # twitchurl
    name_id = str           # "nmplol"

    def __init__(self, **kwargs):        
        self.displayname = kwargs.get('displayname')
        self.language = kwargs.get('language')
        self.links = kwargs.get('links')
        self.logo = kwargs.get('logo')
        self.current_rank = kwargs.get('current_rank')
        self.twitchurl = kwargs.get('twitchurl')
        self.name_id = kwargs.get('name_id')