import json
from typing import Dict, Any

class VodS3Response:
    channel = str
    vod_files = Dict[int, list[str]]
    # vod_files = [ "576354726": [
    #   "Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.json",
    #   "Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.mp3",
    #   "Clip: AF vs. KT - SB vs. DWG [2020 LCK Spring Split]-v576354726.vtt",
    #   "metadata.json"
    # ], ... ]

    def __init__(self, *, channel="", vod_files={}):
        self.channel = channel
        self.vod_files = vod_files

    
