####################################################
#                                                  #
#   !!!  PUSH TO GIT BEFORE BUILDING !!            #
#   !!!  PUSH TO GIT BEFORE BUILDING !!            #
#   !!!  PUSH TO GIT BEFORE BUILDING !!            #
#                                                  #
####################################################
# Preper
docker build --build-arg ENV_TYPE=dev  --no-cache -t cbrodski/preper:official_v2_dev -f Dockerfile_ECS_preper  .
docker push cbrodski/preper:official_v2_dev

# Downloader
docker build --build-arg ENV_TYPE=dev  --no-cache -t cbrodski/downloader:official_v2_dev -f Dockerfile_ECS_downloader  .
docker push cbrodski/downloader:official_v2_dev

# Transcriber
docker build --build-arg ENV_TYPE=dev  --no-cache -t cbrodski/transcriber:official_v2_dev -f Dockerfile_transcriber_faster_whisper  .
docker push cbrodski/transcriber:official_v2_dev