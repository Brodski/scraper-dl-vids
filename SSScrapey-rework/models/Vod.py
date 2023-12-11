import json
import urllib
import env_file as env_varz
from typing import Dict, Any

class Vod:
    channel = str
    id = str
    title = str
    link_s3 = str
    link_s3_vtt = str
    link_s3_json = str
    language = str

    def __init__(self, *, channel="", id="", title="", link_s3="", language="", link_s3_vtt="", link_s3_json=""):
        self.channel = channel
        self.id = id
        self.title = title
        self.link_s3 = link_s3
        if (link_s3 == "" and title != "" and channel != ""):
            self.link_s3 = self.create_link_s3()

        # if (self.link_s3 != "" and self.link_s3_vtt != ""):
        #     self.link_s3_vtt = self.link_s3.rsplit(".", 1)[0] + ".vtt"
        #     self.link_s3_json = self.link_s3.rsplit(".", 1)[0] + ".json"

    def create_link_s3(self):
        vod_encode = urllib.parse.quote(self.title)
        vod_path = env_varz.S3_CAPTIONS_KEYBASE + self.channel + "/" + self.id + "/" + vod_encode
        return env_varz.BUCKET_DOMAIN + "/" + vod_path

