from dotenv import dotenv_values, load_dotenv

env_vars = dotenv_values('.env_public')
load_dotenv()

# this directory legit exists in this bucket ^
BUCKET_NAME = env_vars['BUCKET_NAME']
BUCKET_DOMAIN = env_vars['BUCKET_DOMAIN']
S3_COMPLETED_TODO_AUDIO = env_vars['S3_COMPLETED_TODO_AUDIO']
S3_COMPLETED_CAPTIONS_DONE = env_vars['S3_COMPLETED_CAPTIONS_DONE']
S3_COMPLETED_CAPTIONS_UPLOADED = env_vars['S3_COMPLETED_CAPTIONS_UPLOADED']
S3_CAPTIONS_KEYBASE = env_vars['S3_CAPTIONS_KEYBASE']

A2T_ASSETS_AUDIO = env_vars['A2T_ASSETS_AUDIO']
A2T_ASSETS_CAPTIONS = env_vars['A2T_ASSETS_CAPTIONS']

WHSP_MODEL_SIZE = env_vars['WHSP_MODEL_SIZE']
WHSP_COMPUTE_TYPE = env_vars['WHSP_COMPUTE_TYPE']
WHSP_CPU_THREADS = env_vars['WHSP_CPU_THREADS']
IS_DEBUG = env_vars['IS_DEBUG']
