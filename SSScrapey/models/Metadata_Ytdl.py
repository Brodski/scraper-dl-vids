import json
from typing import Dict, Any

class Metadata_Ytdl:

    def __init__(self, channel: str, displayname: str, language: str, logo: str, twitchurl: str, link: str, metadata: Dict[Any, Any]):
        self.channel = channel    # lolgeranmio
        self.displayname = displayname
        self.language = language
        self.logo = logo
        self.twitchurl = twitchurl

        self.link = link # 1718349481
        self.metadata = metadata
        


    def toJSON(self):
        return {
                "channel": self.channel,
                "link": self.link,
                "metadata":str(self.metadata)
                }
        # return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)
    
    def getFilePathFromMetaD(self):
        for requested in self.metadata.get('requested_downloads', []):
            print(requested.get('format_id', {}))
            if requested.get('format_id') == "Audio_Only": # TODO othe audio_ids like youtube's, ect
                __finaldir = requested.get('__finaldir') # "C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids"
                filepath = requested.get("filepath")     # "C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids\\Bootcamp to Challenger \uff5c-v1747933567.f_Audio_Only.mp3"
                filename = filepath.replace(__finaldir, "")
                filename = filename[1:] if (filename[0] == "/" or filename[0] == "\\") else filename # filename = "Bootcamp to Challenger \uff5c-v1747933567.f_Audio_Only.mp3"

                # ffmpeg convertion to audio doesnt change extension -.-
                filename = (filename[:-4] + ".mp3") if filename[-4:] == ".mp4" else filename # NOTE position of ":" is diff
