import logging
from dotenv import dotenv_values, load_dotenv
import os
import sys
import argparse

print("IN ENV_FILE")

class EnvVars:
    def __init__(self):
        self.DWN_IS_SHORT_DEV_DL = None
        self.DWN_BATCH_SIZE = None
        self.DWN_BATCH_SIZE_OVERRIDE = None
        self.DWN_IS_SKIP_COMPRESS_AUDIO = None
        self.PREP_SELENIUM_IS_HEADLESS = None
        self.PREP_SULLY_DAYS = None
        self.PREP_NUM_CHANNELS = None
        self.PREP_NUM_CHANNELS_OVERRIDE = None
        self.PREP_NUM_VOD_PER_CHANNEL = None
        self.PREP_NUM_VOD_PER_CHANNEL_OVERRIDE  = None
        self.WHSP_A2T_ASSETS_AUDIO = None
        self.WHSP_A2T_ASSETS_CAPTIONS = None
        self.WHSP_COMPUTE_TYPE = None
        self.WHSP_CPU_THREADS = None
        self.WHSP_MODEL_SIZE = None
        self.WHSP_IS_CLOUDWATCH = None
        self.WHSP_IS_BIG_FILES_ENABLED = None
        self.TRANSCRIBER_NUM_INSTANCES = None
        self.TRANSCRIBER_VODS_PER_INSTANCE = None
        self.TRANSCRIBER_INSTANCE_CNT = None
        self.BUCKET_DOMAIN = None
        self.BUCKET_NAME = None
        self.DEBUG_LEVEL = None
        self.IS_VIP_LIST = None
        self.IS_VIP_LIST_DEBUG = None
        self.S3_CAPTIONS_KEYBASE = None
        self.ENV = None
        self.DATABASE = None
        self.DATABASE_HOST = None
        self.DATABASE_USERNAME = None
        self.DATABASE_PASSWORD = None
        self.DATABASE_PORT = None
        self.TWITCH_CLIENT_ID = None
        self.TWITCH_CLIENT_SECRET = None
        #
        self.LOCAL_GPU_RUN = None
        self.DWN_IS_SKIP_DONT_DELETE = None



    def init_argz(self):        
        parser = argparse.ArgumentParser(description="argparse baby")

        ######################################################
        # COPY AND PASTED VARIABLES FROM CONFIG FILE/EnvVars #
        ######################################################
        parser.add_argument("--dwn_is_short_dev_dl", action="store_true")
        parser.add_argument("--dwn_batch_size")
        parser.add_argument("--dwn_is_skip_compress_audio", action="store_true")
        parser.add_argument("--prep_selenium_is_headless")
        parser.add_argument("--prep_sully_days")
        parser.add_argument("--prep_num_channels")
        parser.add_argument("--prep_num_vod_per_channel")
        parser.add_argument("--whsp_a2t_assets_audio")
        parser.add_argument("--whsp_a2t_assets_captions")
        parser.add_argument("--whsp_compute_type")
        parser.add_argument("--whsp_cpu_threads")
        parser.add_argument("--whsp_model_size")
        parser.add_argument("--whsp_is_cloudwatch")
        parser.add_argument("--whsp_is_big_files_enabled")
        parser.add_argument("--transcriber_num_instances")
        parser.add_argument("--transcriber_vods_per_instance")
        parser.add_argument("--transcriber_instance_cnt")
        parser.add_argument("--bucket_domain")
        parser.add_argument("--bucket_name")
        parser.add_argument("--debug_level")
        parser.add_argument("--is_vip_list")
        parser.add_argument("--is_vip_list_debug")
        parser.add_argument("--s3_captions_keybase")
        parser.add_argument("--env")
        parser.add_argument("--database")
        parser.add_argument("--database_host")
        parser.add_argument("--database_username")
        parser.add_argument("--database_password")
        parser.add_argument("--database_port")
        parser.add_argument("--twitch_client_id")
        parser.add_argument("--twitch_client_secret")
        
        ################################
        # FLAGS NOT IN THE CONFIG FILE #
        ################################
        parser.add_argument("--dwn_query_todo", action="store_true", help="prints result of the x most recent vods from every channel")

        ### BAM 0 ###
        args = parser.parse_args()
        self.dwn_query_todo = args.dwn_query_todo
        
        #########
        # BAM 1 #
        #########
        self.init_argz_more(args)


        ##################################################################
        ### I AM THE BEST                                                #
        ### Uses reflection to update all env_varz values from the args  #
        ##################################################################
        for key, value in vars(args).items():
            if value and hasattr(self, key.upper()):
                setattr(self, key.upper(), value)


    def init_argz_more(self, args):
        ###################################
        # LOAD SECRET SENSITIVE VARIABLES #
        ###################################
        # NOTE: 
        # some prod variables passed from terraform ---> lambda
        sensitive_vars_local_path = "./.env"
        sensitive_vars_dev_path   = "./.env"
        sensitive_vars_prod_path  = "./.env_prod"

        # Doing it here
        if args.env is None and os.getenv("ENV") is None:
            print("🛑 WE NEED `ENV`. ENDING")
            sys.exit(1)
        os.environ['ENV'] = os.getenv("ENV") if os.getenv("ENV") else args.env

        print("Envrionment is: ", os.getenv("ENV"))
        if os.getenv("ENV") == "local":
            env_vars = dotenv_values('.env_public_local')
            load_dotenv(sensitive_vars_local_path, override=True)
        elif os.getenv("ENV") == "dev":
            env_vars = dotenv_values('.env_public_dev')
            load_dotenv(sensitive_vars_dev_path, override=True)
        elif os.getenv("ENV") == "prod":
            env_vars = dotenv_values('.env_public_prod')
            load_dotenv(sensitive_vars_prod_path, override=True)
        else:
            print("ENV is None! NEED ENV")
            sys.exit(1) 


        #########################
        # LOAD PUBLIC VARIABLES #
        # idk why i did this    #
        #########################
        self.DWN_IS_SHORT_DEV_DL            = env_vars['DWN_IS_SHORT_DEV_DL']
        self.DWN_BATCH_SIZE                 = env_vars['DWN_BATCH_SIZE']
        self.DWN_IS_SKIP_COMPRESS_AUDIO     = env_vars['DWN_IS_SKIP_COMPRESS_AUDIO']
        self.DWN_BATCH_SIZE_OVERRIDE        = os.getenv('DWN_BATCH_SIZE_OVERRIDE')
        self.PREP_SELENIUM_IS_HEADLESS      = env_vars['PREP_SELENIUM_IS_HEADLESS']
        self.PREP_SULLY_DAYS                = env_vars['PREP_SULLY_DAYS']
        self.PREP_NUM_CHANNELS              = env_vars['PREP_NUM_CHANNELS']
        self.PREP_NUM_CHANNELS_OVERRIDE     = os.getenv('PREP_NUM_CHANNELS_OVERRIDE')
        self.PREP_NUM_VOD_PER_CHANNEL       = env_vars['PREP_NUM_VOD_PER_CHANNEL']
        self.PREP_NUM_VOD_PER_CHANNEL_OVERRIDE  = os.getenv('PREP_NUM_VOD_PER_CHANNEL_OVERRIDE')
        self.WHSP_A2T_ASSETS_AUDIO          = "./assets/audio/"
        self.WHSP_A2T_ASSETS_CAPTIONS       = "./assets/captions/"
        self.WHSP_COMPUTE_TYPE              = env_vars['WHSP_COMPUTE_TYPE']
        self.WHSP_CPU_THREADS               = env_vars['WHSP_CPU_THREADS']
        self.WHSP_MODEL_SIZE                = env_vars['WHSP_MODEL_SIZE']
        self.WHSP_IS_CLOUDWATCH             = env_vars['WHSP_IS_CLOUDWATCH']
        self.WHSP_IS_BIG_FILES_ENABLED      = env_vars['WHSP_IS_BIG_FILES_ENABLED']
        self.TRANSCRIBER_NUM_INSTANCES      = int(os.getenv("TRANSCRIBER_NUM_INSTANCES") if os.getenv("TRANSCRIBER_NUM_INSTANCES") else 1)
        self.TRANSCRIBER_VODS_PER_INSTANCE  = os.getenv("TRANSCRIBER_VODS_PER_INSTANCE")
        self.TRANSCRIBER_INSTANCE_CNT       = os.getenv("TRANSCRIBER_INSTANCE_CNT") if os.getenv("TRANSCRIBER_INSTANCE_CNT") else ""
        self.BUCKET_DOMAIN              = env_vars['BUCKET_DOMAIN']
        self.BUCKET_NAME                = env_vars['BUCKET_NAME']
        self.DEBUG_LEVEL                = env_vars['DEBUG_LEVEL']
        self.IS_VIP_LIST                = env_vars['IS_VIP_LIST']
        self.IS_VIP_LIST_DEBUG          = env_vars['IS_VIP_LIST_DEBUG']
        self.S3_CAPTIONS_KEYBASE        = env_vars['S3_CAPTIONS_KEYBASE']
        self.TWITCH_CLIENT_ID           = os.getenv('TWITCH_CLIENT_ID')
        self.TWITCH_CLIENT_SECRET       = os.getenv('TWITCH_CLIENT_SECRET')

        ###############################################
        # "RELOAD" VARIABLES - from Terraform or .env #
        # b/c its nice to find variables via inteli-sense instead of os.getenv("string")
        ###############################################
        self.ENV                = os.getenv("ENV")
        self.DATABASE           = os.getenv("DATABASE")
        self.DATABASE_HOST      = os.getenv("DATABASE_HOST")
        self.DATABASE_USERNAME  = os.getenv("DATABASE_USERNAME")
        self.DATABASE_PASSWORD  = os.getenv("DATABASE_PASSWORD")
        self.DATABASE_PORT      = os.getenv("DATABASE_PORT")
        # AWS_ACCESS_KEY_ID not loaded here. idk why
        # AWS_SECRET_ACCESS_KEY not loaded here. idk why

        
        self.PREP_NUM_CHANNELS        = env_varz.PREP_NUM_CHANNELS_OVERRIDE        if env_varz.PREP_NUM_CHANNELS_OVERRIDE        and int(env_varz.PREP_NUM_CHANNELS_OVERRIDE) >= 0        else env_varz.PREP_NUM_CHANNELS
        self.PREP_NUM_VOD_PER_CHANNEL = env_varz.PREP_NUM_VOD_PER_CHANNEL_OVERRIDE if env_varz.PREP_NUM_VOD_PER_CHANNEL_OVERRIDE and int(env_varz.PREP_NUM_VOD_PER_CHANNEL_OVERRIDE) >= 0 else env_varz.PREP_NUM_VOD_PER_CHANNEL
        self.DWN_BATCH_SIZE           = env_varz.DWN_BATCH_SIZE_OVERRIDE           if env_varz.DWN_BATCH_SIZE_OVERRIDE           and int(env_varz.DWN_BATCH_SIZE_OVERRIDE) >= 0           else env_varz.PREP_NUM_VOD_PER_CHANNEL



####################################
# BAM                              #
####################################
env_varz = EnvVars()


