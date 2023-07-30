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

SELENIUM_NUM_CHANNELS = env_vars['SELENIUM_NUM_CHANNELS']
SELENIUM_NUM_CHANNELS_DEBUG = env_vars['SELENIUM_NUM_CHANNELS_DEBUG']
SELENIUM_IS_HEADLESS = env_vars['SELENIUM_IS_HEADLESS']

SULLY_NUM_CHANNELS = env_vars['SULLY_NUM_CHANNELS']
SULLY_NUM_CHANNELS_DEBUG = env_vars['SULLY_NUM_CHANNELS_DEBUG']

YTDL_NUM_CHANNELS = env_vars['YTDL_NUM_CHANNELS']
YTDL_NUM_CHANNELS_DEBUG = env_vars['YTDL_NUM_CHANNELS_DEBUG']
YTDL_VIDS_PER_CHANNEL = env_vars['YTDL_VIDS_PER_CHANNEL']
YTDL_VIDS_PER_CHANNEL_DEBUG = env_vars['YTDL_VIDS_PER_CHANNEL_DEBUG']

WHSP_EXEC_FFMPEG = env_vars['WHSP_EXEC_FFMPEG']

IS_DEBUG = env_vars['IS_DEBUG']
JUST_GERA = env_vars['JUST_GERA']

CUSTOM_MD_SERVER = os.getenv("CUSTOM_MD_SERVER")
CUSTOM_MD_KEY = os.getenv("CUSTOM_MD_KEY")

