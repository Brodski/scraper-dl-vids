# from env_app import *
import env_app as env_varz

print("BUCKET_NAME  ----> " + env_varz.BUCKET_NAME)
print("S3_TEST_DIR  ----> " + env_varz.S3_TEST_DIR)
print("S3_RANKING_RAW  ----> " + env_varz.S3_RANKING_RAW)
print("S3_COMPLETED_AUDIO_UPLOADED  ----> " + env_varz.S3_COMPLETED_AUDIO_UPLOADED)
print("S3_COMPLETED_CAPTIONS_UPLOADED  ----> " + env_varz.S3_COMPLETED_CAPTIONS_UPLOADED)
print("S3_ALREADY_DL_KEYBASE  ----> " + env_varz.S3_ALREADY_DL_KEYBASE)
print("S3_CAPTIONS_KEYBASE  ----> " + env_varz.S3_CAPTIONS_KEYBASE)