####################################################
#                                                  #
#   !!!  PUSH TO GIT BEFORE BUILDING !!            #
#   !!!  PUSH TO GIT BEFORE BUILDING !!            #
#   !!!  PUSH TO GIT BEFORE BUILDING !!            #
#                                                  #
####################################################
# Preper
docker build --build-arg ENV_TYPE=prod --no-cache -t cbrodski/preper:official_v2_prod -f Dockerfile_ECS_preper  .
docker push cbrodski/preper:official_v2_prod

# Downloader
docker build --build-arg ENV_TYPE=prod --no-cache -t cbrodski/downloader:official_v2_prod -f Dockerfile_ECS_downloader  .
docker push cbrodski/downloader:official_v2_prod

# Transcriber
docker build --build-arg ENV_TYPE=prod --no-cache -t cbrodski/transcriber:official_v2_prod -f Dockerfile_transcriber_faster_whisper  .
docker push cbrodski/transcriber:official_v2_prod