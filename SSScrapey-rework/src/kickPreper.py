
import os
import controllers.MicroPreper.preperGo as preperGo
from env_file import env_varz


#####################################################
# FILE INFO                                         #
#####################################################
# Does everything.
# API sully gnome - Gets top channels 
# Selenium  - gets vods
# ytdl      - downloads new vods
# ffmpeg    - compresses audio
# S3        - uploads audio
# S3        - updates completed json


######################################################
# BEGIN                                              #
######################################################
if __name__ == "__main__":
    env_varz.init_argz()
    preperGo.prepare()