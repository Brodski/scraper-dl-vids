from dotenv import dotenv_values, load_dotenv
import os

env_vars = dotenv_values('.env_public')
load_dotenv()

BUCKET_NAME = env_vars['BUCKET_NAME']
BUCKET_DOMAIN = env_vars['BUCKET_DOMAIN']

S3_TEST_DIR = env_vars['S3_TEST_DIR'] 
S3_RANKING_RAW = env_vars["S3_RANKING_RAW"]
S3_COMPLETED_CAPTIONS_JSON = env_vars['S3_COMPLETED_CAPTIONS_JSON']
S3_COMPLETED_TODO_AUDIO = env_vars['S3_COMPLETED_TODO_AUDIO']
S3_OVERVIEW_STATE_JSON = env_vars['S3_OVERVIEW_STATE_JSON']
S3_OVERVIEW_STATE_LIGHT_JSON = env_vars['S3_OVERVIEW_STATE_LIGHT_JSON']
S3_COMPLETED_INDIV_CHAN_ROOT = env_vars['S3_COMPLETED_INDIV_CHAN_ROOT']
S3_ALREADY_DL_KEYBASE = env_vars['S3_ALREADY_DL_KEYBASE']
S3_CAPTIONS_KEYBASE = env_vars['S3_CAPTIONS_KEYBASE']
S3_CUSTOM_METADATA_KEYBASE = env_vars['S3_CUSTOM_METADATA_KEYBASE']

SELENIUM_NUM_CHANNELS = env_vars['SELENIUM_NUM_CHANNELS']
SELENIUM_IS_HEADLESS = env_vars['SELENIUM_IS_HEADLESS']
SELENIUM_NUM_VODS = env_vars['SELENIUM_NUM_VODS']

SULLY_NUM_CHANNELS = env_vars['SULLY_NUM_CHANNELS']
YTDL_NUM_CHANNELS = env_vars['YTDL_NUM_CHANNELS']
YTDL_VIDS_PER_CHANNEL = env_vars['YTDL_VIDS_PER_CHANNEL']
WHSP_EXEC_FFMPEG = env_vars['WHSP_EXEC_FFMPEG']
JUST_GERA = env_vars['JUST_GERA']
A2T_ASSETS_AUDIO = env_vars['A2T_ASSETS_AUDIO']
A2T_ASSETS_CAPTIONS = env_vars['A2T_ASSETS_CAPTIONS']
WHSP_MODEL_SIZE = env_vars['WHSP_MODEL_SIZE']
WHSP_COMPUTE_TYPE = env_vars['WHSP_COMPUTE_TYPE']
WHSP_CPU_THREADS = env_vars['WHSP_CPU_THREADS']
SSL_FILE = env_vars['SSL_FILE']

CUSTOM_MD_SERVER = os.getenv("CUSTOM_MD_SERVER")
ENV = os.getenv("ENV")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE = os.getenv("DATABASE")


# Overwrite the vars
# This could be better :thinking:
if os.getenv("ENV") == "local":
    print("YES IAS LOCAAAAAAAALLLLLLL")
    print("YES IAS LOCAAAAAAAALLLLLLL")
    print("YES IAS LOCAAAAAAAALLLLLLL")
    print("YES IAS LOCAAAAAAAALLLLLLL")
    print("YES IAS LOCAAAAAAAALLLLLLL")
    env_vars_local = dotenv_values('.env_public_dev')
    BUCKET_NAME  = env_vars_local['BUCKET_NAME']
    BUCKET_DOMAIN  = env_vars_local['BUCKET_DOMAIN']
    SULLY_NUM_CHANNELS = env_vars_local['SULLY_NUM_CHANNELS']
    SELENIUM_NUM_CHANNELS = env_vars_local['SELENIUM_NUM_CHANNELS']
    SELENIUM_IS_HEADLESS = env_vars_local['SELENIUM_IS_HEADLESS']
    YTDL_NUM_CHANNELS = env_vars_local['YTDL_NUM_CHANNELS']
    YTDL_VIDS_PER_CHANNEL = env_vars_local['YTDL_VIDS_PER_CHANNEL']
    WHSP_EXEC_FFMPEG  = env_vars_local['WHSP_EXEC_FFMPEG']
    IS_DEBUG = env_vars_local['IS_DEBUG']
    WHSP_MODEL_SIZE = env_vars_local['WHSP_MODEL_SIZE']
    WHSP_COMPUTE_TYPE = env_vars_local['WHSP_COMPUTE_TYPE']
    WHSP_CPU_THREADS = env_vars_local['WHSP_CPU_THREADS']
    SSL_FILE = env_vars_local['SSL_FILE']