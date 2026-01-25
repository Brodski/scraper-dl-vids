# ############################################
#
#                  CONFIGS 
# Instance most be greater/less than these:
#
# ############################################
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    print("We are in lambda")


class Configz:
    def __init__(self):
        self.VAST_API_KEY                  = os.environ.get('VAST_API_KEY')
        self.TRANSCRIBER_NUM_INSTANCES     = int(os.environ.get('TRANSCRIBER_NUM_INSTANCES'))
        self.TRANSCRIBER_VODS_PER_INSTANCE = int(os.environ.get('TRANSCRIBER_VODS_PER_INSTANCE'))
        self.TRANSCRIBER_MODEL_SIZE_OVERRIDE = os.environ.get('TRANSCRIBER_MODEL_SIZE_OVERRIDE')
        self.AWS_SECRET_ACCESS_KEY         = os.environ.get('MY_AWS_SECRET_ACCESS_KEY')
        self.AWS_ACCESS_KEY_ID             = os.environ.get('MY_AWS_ACCESS_KEY_ID')
        self.ENV                           = os.environ.get('ENV')
        self.DATABASE_HOST                 = os.environ.get('DATABASE_HOST')
        self.DATABASE_USERNAME             = os.environ.get('DATABASE_USERNAME')
        self.DATABASE_PASSWORD             = os.environ.get('DATABASE_PASSWORD')
        self.DATABASE_PORT                 = os.environ.get('DATABASE_PORT')
        self.DATABASE                      = os.environ.get('DATABASE')
        self.DOCKER                        = os.environ.get('DOCKER') # or "cbrodski/transcriber:official_v2"

        self.dph            = "0.30"  # 0.30 dollars / hour            
                                      # dph = "0.12"
        self.dph_min        = "0.04"  # 0.04 dollars / hour            
        self.cuda_vers      = "12"
        self.cpu_ram        = "16000.0"
        self.disk_space     = "32"
        self.disk           = 32.0                                                      # Gb
        self.image          = self.DOCKER
        self.storage_cost   = "0.3"
        self.blacklist_gpus = ["GTX 1070", "RTX 2080 Ti", "GTX 1080 Ti", "RTX 2070S", "NVIDIA RTX PRO 4000 Blackwell", "NVIDIA RTX PRO 4000 Blackwell", "RTX PRO 4000" ] # Container not built for Blackwell -> "ERROR Transcribing vod: cuBLAS failed with status CUBLAS_STATUS_NOT_SUPPORTED"
        self.blacklist_ids  = []
        self.inet_down_cost = "0.05"
        self.inet_up_cost   = "0.05"
        self.gpu_ram        = "23000"

####################################
# BAM                              #
####################################
configz = Configz()