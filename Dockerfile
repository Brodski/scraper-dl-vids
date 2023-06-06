FROM nvidia/cuda:12.0.0-devel-ubuntu20.04 

# Need devel for cudnn https://github.com/NVIDIA/nvidia-docker/issues/1160#issuecomment-568814500

##############################################
# - Build
# docker build -t coolimage:3.5 .
# - WINDOWS
# docker run -v /host/path:/container/path -it coolimage:latest  /bin/bash
# docker run -v C:\Users\BrodskiTheGreat\Desktop\desktop\Code\scraper-dl-vids\outputz-temp:/app/scraper-dl-vids/docker-benchmarks -it coolimage:3.5  /bin/bash
# - LINUX
# mkdir -p /var/log/benchy
# docker run -v /var/log/benchy:/app/scraper-dl-vids/docker-benchmarks <image_name>
###############################################
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#install-guide
# https://docs.docker.com/engine/install/
#############################################
# RUN THIS ON HOST !!!
#############################################
# install docker
# for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do apt-get remove $pkg; done &&
# apt-get update &&
# apt-get install ca-certificates curl gnupg -y &&
# install -m 0755 -d /etc/apt/keyrings &&
# curl -fsSL https://download.docker.com/linux/ubuntu/gpg |  gpg --dearmor -o /etc/apt/keyrings/docker.gpg &&
# chmod a+r /etc/apt/keyrings/docker.gpg &&
# echo \
#   "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
#   "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
#   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null && 
# apt-get update &&
# apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

# # install nvidia container toolkit
# systemctl --now enable docker 
# distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
#       && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
#       && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
#             sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
#             tee /etc/apt/sources.list.d/nvidia-container-toolkit.list &&
# apt-get update &&
# apt-get install -y nvidia-container-toolkit &&
# nvidia-ctk runtime configure --runtime=docker &&
# systemctl restart docker 

##############################################
ENV BENCH_OUTPUT="/app/scraper-dl-vids/docker-benchmarks"
ENV BARBARA="BarbaraWalters.mp3"
ENV GPT_PODCAST="OPENASSISTANT+TAKES+ON+CHATGPT.mp3"

RUN echo "My variable: $BENCH_OUTPUT"
RUN echo "My variable: $BENCH_OUTPUT"
RUN echo "My variable: $BENCH_OUTPUT"
RUN echo "My variable: $BENCH_OUTPUT"
RUN echo "My variable: $BENCH_OUTPUT"

# ##########
# # Python #
# ##########
WORKDIR /app
RUN apt update \
    && apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev -y \
    && apt install curl -y \
    && curl https://www.python.org/ftp/python/3.10.10/Python-3.10.10.tgz -o Python-3.10.10.tgz \
    && tar -xzf Python-3.10.10.tgz \
    && cd Python-3.10.10/ \
    && ./configure --enable-optimizations --with-ensurepip=install \
    && make -j $(nproc) \
    && make altinstall \
    && ln -s /usr/local/bin/python3.10 /usr/local/bin/python \
    && cd .. \
    && rm Python-3.10.10.tgz 

# #######
# # Pip #
# #######
WORKDIR /app
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
      && python get-pip.py pip==23.0.1 \
      && pip --version \
      && rm get-pip.py 

# ###########
# # Project #
# ###########
# 1st RUN to fix a goofy error -> https://github.com/docker/docs/issues/13980
# https://wiki.debian.org/SourcesList
WORKDIR /app
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata  \
    && echo "deb http://deb.debian.org/debian bullseye main" >> /etc/apt/sources.list \
    && echo "deb-src http://deb.debian.org/debian bullseye main" >> /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian-security/ bullseye-security main" >> /etc/apt/sources.list \
    && echo "deb-src http://deb.debian.org/debian-security/ bullseye-security main" >> /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian bullseye-updates main" >> /etc/apt/sources.list \
    && echo "deb-src http://deb.debian.org/debian bullseye-updates main" >> /etc/apt/sources.list
RUN apt install git-all -y \
    && git clone https://github.com/Brodski/scraper-dl-vids.git \
    #   && cd scraper-dl-vids/ \
    #   && python -m pip install virtualenv \
    #   && python -m virtualenv venv \
    #   && source venv/bin/activate 
      && pip install faster-whisper \
      && pip install -U openai-whisper 
    #   && deactivate


# For testing
WORKDIR /app/scraper-dl-vids/audio2Text/assets/audio
RUN  wget https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/testz/OPENASSISTANT+TAKES+ON+CHATGPT.mp3




WORKDIR /app/scraper-dl-vids/audio2Text
RUN mkdir -p $BENCH_OUTPUT
# CMD echo "My BENCH_OUTPUTZ: $BENCH_OUTPUT"
RUN echo "OUTPUT TO $BENCH_OUTPUT"
RUN echo "OUTPUT TO $BENCH_OUTPUT"
RUN echo "OUTPUT TO $BENCH_OUTPUT"
RUN echo "OUTPUT TO $BENCH_OUTPUT"

# https://github.com/NVIDIA/nvidia-docker/issues/1644
RUN echo "LD_LIBRARY_PATH $LD_LIBRARY_PATH"
# RUN export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda-12.0/targets/x86_64-linux/lib/"
# RUN export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib/python3.10/site-packages/nvidia/cudnn/lib/"
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib/python3.10/site-packages/nvidia/cudnn/lib/"
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/cuda-12.0/targets/x86_64-linux/lib/"
RUN echo "LD_LIBRARY_PATH $LD_LIBRARY_PATH"

CMD python ./gogoWhisperFAST.py -f    "$BARBARA" -m "tiny"      > $BENCH_OUTPUT/tiny-barbara.txt  2>&1 \
    && python ./gogoWhisperFAST.py -f "$BARBARA" -m "small"     > $BENCH_OUTPUT/small-barbara.txt 2>&1 \
    && python ./gogoWhisperFAST.py -f "$GPT_PODCAST" -m "tiny"  > $BENCH_OUTPUT/tiny-chatgpt.txt  2>&1 \
    && python ./gogoWhisperFAST.py -f "$GPT_PODCAST" -m "small" > $BENCH_OUTPUT/small-chatgpt.txt 2>&1 

















#########
# cuDNN #
#########
# WORKDIR /app
# RUN curl 'https://developer.nvidia.com/downloads/compute/cudnn/secure/8.9.1/local_installers/12.x/cudnn-local-repo-debian11-8.9.1.23_1.0-1_amd64.deb/' \
#     -H 'cookie: AMCV_F207D74D549850760A4C98C6%40AdobeOrg=1176715910%7CMCMID%7C71794017538113168927256794386408995986%7CMCAID%7CNONE%7CvVersion%7C5.4.0; at_check=true; nvweb_A=3a20aa19-c4d1-4220-aa0c-4e3417062d0d; nv_country_code=US; nvidiaCart={"cart":[],"lastAction":null}; s_fid=3A0A7C8FDD401624-389B99CDF8EF59F0; SESSls=gseo; SESSlsd=https%3A%2F%2Fwww.google.com%2F; SESSloginhint=cbrodski%40gmail.com; SESSauthn=1; nvweb_E=Ng0muRbpGfwOlHdK11fODOxuBWW-xjsvDS9pwvBA6M6BTDMUS2X5Py3WvbzbBWIxaalcbe9oUzfKUzzkHOX7Yg; nvweb_S=77SfVgBdKv2IUdfq0Ta6rsUNgJFeD5eXW26lD3BmW3nRBjQUseguZchvA_2fylO8eCa4bSe4HtAdtU3-vA747Q; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3pOak00TlRBd1hTd2laWEJhUlVNMWNHTXRjM2g0TFY5WFdWRm1OM1FpTENJeE5qZ3pNalkyTXpreExqVXlOek01T0NKZCIsImV4cCI6IjIwMjMtMDUtMTlUMDU6NTk6NTEuNTI3WiIsInB1ciI6ImNvb2tpZS5yZW1lbWJlcl91c2VyX3Rva2VuIn19--6e4d0e90a73dae9c6c4de73c96594d3112f0cb5a; _devzone_session=c3f0c67e57d0c1dc8b76c908a47deee2; SSESS2088448faf607a381892ca97487fa4c7=OgiRpvCKlv11kRU4V4mjNQk0e9SGrua9nSbVEEuLpRU; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+05+2023+01%3A08%3A50+GMT-0600+(Mountain+Daylight+Time)&version=6.23.0&hosts=&consentId=2594bb82-8cee-4b85-b314-a83e40044968&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0004%3A0%2CC0003%3A0&AwaitingReconsent=false; mbox=PC#94bacd6001d54eec8f98820bb1a81072.35_0#1746515331|session#05995f980d7c4749a90c107ac01baaba#1683272391' \
#     -H 'dnt: 1' \
#     -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36' \
#     --compressed \
#     -L --output cudnn-local-repo-debian11-8.9.1.23_1.0-1_amd64.deb \ 
#     && dpkg -i cudnn-local-repo-debian11-8.9.1.23_1.0-1_amd64.deb  \
#     && apt install ./cudnn-local-repo-debian11-8.9.1.23_1.0-1_amd64.deb \
#     && cp /var/cudnn-local-repo-*/cudnn-local-*-keyring.gpg /usr/share/keyrings/ \
#     && apt-get update \
#     && apt-get install libcudnn8=8.9.1.23-1+cuda12.1 \
#     && apt-get install libcudnn8-dev=8.9.1.23-1+cuda12.1 \
#     && rm cudnn-local-repo-debian11-8.9.1.23_1.0-1_amd64.deb 