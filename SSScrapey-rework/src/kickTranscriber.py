from env_file import env_varz
env_varz.init_argz()
# ↑            
# ↑ 
# ↑ 
# THIS MUST BE AT THE VERY VERY VERY START B/C PYTHON IS A JOKE
#
import controllers.MicroTranscriber.transcriberGo as transcriberGo
from env_file import env_varz


if __name__ == "__main__":
    print("transcriberGo gogogo!")
    transcriberGo.goTranscribeBatch(False)