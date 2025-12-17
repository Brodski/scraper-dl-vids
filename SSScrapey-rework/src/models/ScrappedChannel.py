import json
from typing import Dict, Any

class ScrappedChannel:
    name_id      = str   # "nmplol"
    displayname  = str   # "Nmplol"
    language     = str   # "English"
    links        = list[str]   # ["/videos/40792901", "/videos/1470165627"],
    logo         = str   # "https://static-cdn.jtvnw.net/jtv_user_pictures/e4d9bf96-311d-487a-b5eb-9f9a94e0f795-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
    current_rank = int   # 22
    twitchurl    = str   # twitchurl

    viewminutes     = int
    streamedminutes = int
    maxviewers      = int
    avgviewers      = int
    followers       = int
    followersgained = int

    partner         = bool
    affiliate       = bool
    mature          = bool

    previousviewminutes     = int
    previousstreamedminutes = int
    previousmaxviewers      = int
    previousavgviewers      = int
    previousfollowergain    = int

    def __init__(self, **kwargs):        
        self.name_id                 = kwargs.get('name_id')
        self.displayname             = kwargs.get('displayname')
        self.language                = kwargs.get('language')
        self.links                   = kwargs.get('links')
        self.logo                    = kwargs.get('logo')
        self.current_rank            = kwargs.get('current_rank')
        self.twitchurl               = kwargs.get('twitchurl')
        self.viewminutes             = kwargs.get('viewminutes')
        self.streamedminutes         = kwargs.get('streamedminutes')
        self.maxviewers              = kwargs.get('maxviewers')
        self.avgviewers              = kwargs.get('avgviewers')
        self.followers               = kwargs.get('followers')
        self.followersgained         = kwargs.get('followersgained')
        self.partner                 = kwargs.get('partner')
        self.affiliate               = kwargs.get('affiliate')
        self.mature                  = kwargs.get('mature')
        self.previousviewminutes     = kwargs.get('previousviewminutes')
        self.previousstreamedminutes = kwargs.get('previousstreamedminutes')
        self.previousmaxviewers      = kwargs.get('previousmaxviewers')
        self.previousavgviewers      = kwargs.get('previousavgviewers')
        self.previousfollowergain    = kwargs.get('previousfollowergain')

    def print(self):
        print(self)
        for attr in dir(self):
            # Filtering out special methods/attributes and methods
            if not attr.startswith("__") and not callable(getattr(self, attr)):
                print(f"    {attr} = {getattr(self, attr)}")