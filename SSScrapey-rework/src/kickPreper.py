import controllers.MicroPreper.preperGo as preperGo

# Does everything.
# API sully gnome - Gets top channels 
# Selenium  - gets vods
# ytdl      - downloads new vods
# ffmpeg    - compresses audio
# S3        - uploads audio
# S3        - updates completed json
if __name__ == "__main__":
    preperGo.prepare()