from env_file import env_varz
env_varz.init_argz()
# ↑            
# ↑ 
# ↑ 
# THIS MUST BE AT THE VERY VERY VERY START B/C PYTHON IS A JOKE
#
import controllers.MicroTranscriber.transcriberGo as transcriberGo
from env_file import env_varz
import threading
import os

def timeout():
    print("Timeout! Exiting.")
    os._exit(1)


if __name__ == "__main__":
    print("transcriberGo gogogo!")
    timer = threading.Timer(43200, timeout)  # 12 hours = 43200 seconds
    timer.start()

    try:
        transcriberGo.goTranscribeBatch(False)
        pass
    finally:
        timer.cancel()