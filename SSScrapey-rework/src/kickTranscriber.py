import controllers.MicroTranscriber.transcriberGo as transcriberGo
from env_file import env_varz


if __name__ == "__main__":
    print("transcriberGo gogogo!")
    env_varz.init_argz()
    transcriberGo.goTranscribeBatch(False)