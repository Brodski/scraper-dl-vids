from dotenv import dotenv_values, load_dotenv
import os
import sys

load_dotenv()
print('os.getenv("ENV"):', os.getenv("ENV"))
print('os.getenv("ENV"):', os.getenv("ENV"))
print('os.getenv("ENV"):', os.getenv("ENV"))
print('os.getenv("ENV"):', os.getenv("ENV"))
print('os.getenv("ENV"):', os.getenv("ENV"))

dotenv_prod_path ="./env_prod"
if os.getenv("ENV") == "local":
    env_vars = dotenv_values('.env_public_local')
elif os.getenv("ENV") == "dev":
    env_vars = dotenv_values('.env_public_dev')
    env_vars['SSL_FILE'] = "/app/scraper-dl-vids/SSScrapey-rework/cacert-2023-08-22.pem"
elif os.getenv("ENV") == "prod":
    env_vars = dotenv_values('.env_public_prod')
    env_vars['SSL_FILE'] = "/app/scraper-dl-vids/SSScrapey-rework/cacert-2023-08-22.pem"
    try:
        load_dotenv(dotenv_prod_path, override=True)
    except Exception as e:
        print("failed to load dotenv")
        print(str(e))
    # variables passed from terraform > lambda
    print("PROD")
    print("PROD")
    print("PROD")
    print("PROD")
    print('ENV: ' + os.getenv("ENV"))
    print('ENV: ' + os.getenv("ENV"))
    print('DATABASE_HOST: ' + os.getenv("DATABASE_HOST"))
    print('DATABASE: ' + os.getenv("DATABASE"))

else:
    print("ENV is None! NEED ENV")
    sys.exit(1)  # Exit the script with an error code




DWN_BATCH_SIZE = env_vars['DWN_BATCH_SIZE']
DWN_COMPRESS_AUDIO = env_vars['DWN_COMPRESS_AUDIO']
DWN_QUERY_PER_RECENT = env_vars['DWN_QUERY_PER_RECENT']
DWN_IS_SHORT_DEV_DL = env_vars['DWN_IS_SHORT_DEV_DL']

PREP_DB_UPDATE_VODS_NUM = env_vars['PREP_DB_UPDATE_VODS_NUM']
PREP_SELENIUM_IS_HEADLESS = env_vars['PREP_SELENIUM_IS_HEADLESS']
PREP_SELENIUM_NUM_CHANNELS = env_vars['PREP_SELENIUM_NUM_CHANNELS']
PREP_SELENIUM_NUM_VODS_PER = env_vars['PREP_SELENIUM_NUM_VODS_PER']
PREP_SULLY_NUM_CHANNELS = env_vars['PREP_SULLY_NUM_CHANNELS']
PREP_SULLY_DAYS = env_vars['PREP_SULLY_DAYS']

WHSP_A2T_ASSETS_AUDIO = env_vars['WHSP_A2T_ASSETS_AUDIO']
WHSP_A2T_ASSETS_CAPTIONS = env_vars['WHSP_A2T_ASSETS_CAPTIONS']
WHSP_BATCH_SIZE = env_vars['WHSP_BATCH_SIZE']
WHSP_COMPUTE_TYPE = env_vars['WHSP_COMPUTE_TYPE']
WHSP_CPU_THREADS = env_vars['WHSP_CPU_THREADS']
WHSP_MODEL_SIZE = env_vars['WHSP_MODEL_SIZE']
WHSP_IS_CLOUDWATCH = env_vars['WHSP_IS_CLOUDWATCH']

ENV = os.getenv("ENV")
DATABASE = os.getenv("DATABASE")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DWN_IS_SHORT_DEV_DL = os.getenv("DWN_IS_SHORT_DEV_DL") if os.getenv("DWN_IS_SHORT_DEV_DL") else DWN_IS_SHORT_DEV_DL

BUCKET_DOMAIN = env_vars['BUCKET_DOMAIN']
BUCKET_NAME = env_vars['BUCKET_NAME']
SSL_FILE = env_vars['SSL_FILE']
S3_CAPTIONS_KEYBASE = env_vars['S3_CAPTIONS_KEYBASE']