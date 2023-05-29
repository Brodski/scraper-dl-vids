ssh root@216.155.135.249 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"



#################################################################################
# HOST
#################################################################################
# ????????????????????????????????
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#install-guide
# https://docs.docker.com/engine/install/


# curl https://get.docker.com | sh  # Do not use in production:
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
apt-get update
apt-get install ca-certificates curl gnupg -y
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 
apt-get update 
apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
# sudo docker run hello-world

systemctl --now enable docker 
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            tee /etc/apt/sources.list.d/nvidia-container-toolkit.list &&
apt-get update &&
apt-get install -y nvidia-container-toolkit &&
nvidia-ctk runtime configure --runtime=docker &&
systemctl restart docker 

# Start docker
docker run --rm --runtime=nvidia --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi 
docker run --runtime=nvidia --gpus all cbrodski/audio2text /bin/bash
# docker run --rm --runtime=nvidia --gpus all -it nvidia/cuda:12.0.0-runtime-ubuntu22.04 /bin/bash

#################################################################################
# DOCKER --- nvidia/cuda:12.0.0-devel-ubuntu20.04
#################################################################################
echo "" 
echo "Python" 
echo "" 
export HOMEZ=`pwd`
apt update &&
apt-get update &&
apt install curl -y &&
apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev -y &&
curl https://www.python.org/ftp/python/3.10.10/Python-3.10.10.tgz -o Python-3.10.10.tgz &&
tar -xzf Python-3.10.10.tgz &&
cd Python-3.10.10/ &&
./configure --enable-optimizations --with-ensurepip=install &&
make -j $(nproc) &&
make altinstall &&
ln -s /usr/local/bin/python3.10 /usr/local/bin/python &&
cd .. &&
rm Python-3.10.10.tgz &&


echo "" &&
echo "PIP" &&
echo "" &&
cd $HOMEZ &&
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py &&
python get-pip.py pip==23.0.1 &&
pip --version &&
rm get-pip.py &&


echo "" &&
echo "Project" &&
echo "" &&
cd $HOMEZ &&
DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata &&
apt install git-all -y &&
git clone https://github.com/Brodski/scraper-dl-vids.git &&
cd scraper-dl-vids/ &&
python -m pip install faster-whisper &&
python -m pip install -U openai-whisper 

LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-12.0/targets/x86_64-linux/lib/
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/python3.10/site-packages/nvidia/cudnn/lib/


##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
# Vultr
  # Dvd
  ssh titus@66.135.28.25 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-dvd"
  # classic deb
  ssh root@207.148.28.23 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"
