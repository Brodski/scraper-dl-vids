from dotenv import dotenv_values, load_dotenv
import os
import sys

load_dotenv()

if os.getenv("ENV") == "local":
    env_vars = dotenv_values('.env_public_dev')
elif os.getenv("ENV") == "dev":
    env_vars = dotenv_values('.env_public_dev')
    env_vars['SSL_FILE'] = "/app/scraper-dl-vids/SSScrapey-rework/cacert-2023-08-22.pem"
elif os.getenv("ENV") == "prod":
    env_vars = dotenv_values('.env_public')
else:
    print("ENV is None! NEED ENV")
    sys.exit(1)  # Exit the script with an error code


A2T_ASSETS_AUDIO = env_vars['A2T_ASSETS_AUDIO']
A2T_ASSETS_CAPTIONS = env_vars['A2T_ASSETS_CAPTIONS']
BUCKET_DOMAIN = env_vars['BUCKET_DOMAIN']
BUCKET_NAME = env_vars['BUCKET_NAME']
DWN_QUERY_PER_RECENT = env_vars['DWN_QUERY_PER_RECENT']
DWN_BATCH_SIZE = env_vars['DWN_BATCH_SIZE']
DWN_COMPRESS_AUDIO = env_vars['DWN_COMPRESS_AUDIO']

SELENIUM_IS_HEADLESS = env_vars['SELENIUM_IS_HEADLESS']
SELENIUM_NUM_CHANNELS = env_vars['SELENIUM_NUM_CHANNELS']
SELENIUM_NUM_VODS = env_vars['SELENIUM_NUM_VODS']
SULLY_NUM_CHANNELS = env_vars['SULLY_NUM_CHANNELS']

WHSP_COMPUTE_TYPE = env_vars['WHSP_COMPUTE_TYPE']
WHSP_CPU_THREADS = env_vars['WHSP_CPU_THREADS']
WHSP_EXEC_FFMPEG = env_vars['WHSP_EXEC_FFMPEG']
WHSP_MODEL_SIZE = env_vars['WHSP_MODEL_SIZE']
YTDL_NUM_CHANNELS = env_vars['YTDL_NUM_CHANNELS']
YTDL_VIDS_PER_CHANNEL = env_vars['YTDL_VIDS_PER_CHANNEL']
SSL_FILE = env_vars['SSL_FILE']
S3_CAPTIONS_KEYBASE = env_vars['S3_CAPTIONS_KEYBASE']

ENV = os.getenv("ENV")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE = os.getenv("DATABASE")
