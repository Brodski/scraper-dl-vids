from dotenv import dotenv_values

env_vars = dotenv_values('.env_public')

# this directory legit exists in this bucket ^
BUCKET_NAME = env_vars['BUCKET_NAME']
S3_TEST_DIR = env_vars['S3_TEST_DIR'] 
S3_RANKING_RAW = env_vars["S3_RANKING_RAW"]
S3_COMPLETED_AUDIO_UPLOADED = env_vars['S3_COMPLETED_AUDIO_UPLOADED']
S3_COMPLETED_CAPTIONS_UPLOADED = env_vars['S3_COMPLETED_CAPTIONS_UPLOADED']
S3_ALREADY_DL_KEYBASE = env_vars['S3_ALREADY_DL_KEYBASE']
S3_CAPTIONS_KEYBASE = env_vars['S3_CAPTIONS_KEYBASE']
S3_DOMAIN_WGET = env_vars['S3_DOMAIN_WGET']
A2T_ASSETS_AUDIO = env_vars['A2T_ASSETS_AUDIO']
A2T_ASSETS_CAPTIONS = env_vars['A2T_ASSETS_CAPTIONS']
