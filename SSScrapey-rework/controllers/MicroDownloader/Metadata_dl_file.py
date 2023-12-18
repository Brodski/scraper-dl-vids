import json
from typing import Dict, Any

class Metadata_dl_file:

    def __init__(self, channel: str, displayname: str, language: str, logo: str, twitchurl: str, link: str, outFile: str, metadata: Dict[Any, Any]):
        self.channel = channel    # lolgeranmio
        self.displayname = displayname
        self.language = language
        self.logo = logo
        self.twitchurl = twitchurl
        self.outFile = outFile

        self.link = link # 1718349481
        self.metadata = metadata


    def toJSON(self):
        return {
                "channel": self.channel,
                "link": self.link,
                "metadata":str(self.metadata)
                }
        # return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)
    