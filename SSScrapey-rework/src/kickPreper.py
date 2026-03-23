from env_file import env_varz
env_varz.init_argz()

import controllers.MicroPreper.preperGo as preperGo
import threading
import os



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

def timeout():
    print("Timeout! Exiting.")
    # sys.exit(1)
    print("gg ending with os._exit")
    os._exit(1)

if __name__ == "__main__":
    timer = threading.Timer(5400, timeout)  # 1.5 hours = 5400 seconds
    timer.start()

    try:
        preperGo.prepare()
    finally:
        timer.cancel()