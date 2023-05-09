# import requests
import urllib.request
import os
import time



url = 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/testz/BarbaraWalters.mp3'

filename = os.path.basename(url)

start_time = time.time()

urllib.request.urlretrieve(url, filename)

run_time = time.time() - start_time

print("run_time=" + str(run_time))

'''
# Git
sudo yum update
sudo dnf install git-all -y

# Python
# sudo yum install openssl-devel libffi-devel bzip2-devel -y &&
#
sudo yum groupinstall "Development Tools" -y &&
sudo yum install openssl-devel libffi-devel bzip2-devel zlib-devel sqlite-devel readline-devel xz-devel wget -y &&

cd /home/ssm-user &&
sudo curl -O https://www.python.org/ftp/python/3.10.10/Python-3.10.10.tgz &&
sudo tar -xzf Python-3.10.10.tgz &&
cd Python-3.10.10/ &&
sudo  ./configure --enable-optimizations --with-ensurepip=install &&
sudo make altinstall &&
sudo ln -s /usr/local/bin/python3.10 /usr/local/bin/python &&
cd /home/ssm-user &&
sudo rm Python-3.10.10.tgz
@
# Pip 
# ????????????????????????????
cd /home/ssm-user &&
sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py &&
sudo python get-pip.py pip==23.0.1 &&
pip --version &&
sudo rm get-pip.py &&

# Proj
sudo git clone https://github.com/Brodski/scraper-dl-vids.git &&
cd scraper-dl-vids/ &&
sudo python -m pip install virtualenv &&
sudo python -m virtualenv venv &&
source venv/bin/activate &&
sudo python -m pip install requests  &&
sudo python -m pip install faster-whisper &&
sudo python -m pip install -U openai-whisper

sudo python -m pip install -r requirements.txt
sudo pip install -r requirements.txt  

# FFMPEG
sudo mkdir -v -p /usr/local/bin/ffmpeg &&
cd /usr/local/bin/ffmpeg &&
sudo wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && 
sudo tar -xvf ffmpeg-release-amd64-static.tar.xz --strip-components=1 &&
sudo ln -snf /usr/local/bin/ffmpeg/ffmpeg /usr/bin/ffmpeg &&
sudo ln -snf /usr/local/bin/ffmpeg/ffpropbe /usr/bin/ffpropbe &&
sudo rm -v -f ffmpeg-release-amd64-static.tar.xz



# https://developer.nvidia.com/rdp/cudnn-download






# WORKS 
cd /home/ssm-user/ &&
curl 'https://developer.nvidia.com/downloads/compute/cudnn/secure/8.9.0/local_installers/12.x/cudnn-local-repo-rhel7-8.9.0.131-1.0-1.x86_64.rpm/' \
  -H 'cookie: AMCV_F207D74D549850760A4C98C6%40AdobeOrg=1176715910%7CMCMID%7C71794017538113168927256794386408995986%7CMCAID%7CNONE%7CvVersion%7C5.4.0; at_check=true; nvweb_A=3a20aa19-c4d1-4220-aa0c-4e3417062d0d; nv_country_code=US; nvidiaCart={"cart":[],"lastAction":null}; s_fid=3A0A7C8FDD401624-389B99CDF8EF59F0; SESSls=gseo; SESSlsd=https%3A%2F%2Fwww.google.com%2F; SESSloginhint=cbrodski%40gmail.com; SESSauthn=1; nvweb_E=Ng0muRbpGfwOlHdK11fODOxuBWW-xjsvDS9pwvBA6M6BTDMUS2X5Py3WvbzbBWIxaalcbe9oUzfKUzzkHOX7Yg; nvweb_S=77SfVgBdKv2IUdfq0Ta6rsUNgJFeD5eXW26lD3BmW3nRBjQUseguZchvA_2fylO8eCa4bSe4HtAdtU3-vA747Q; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3pOak00TlRBd1hTd2laWEJhUlVNMWNHTXRjM2g0TFY5WFdWRm1OM1FpTENJeE5qZ3pNalkyTXpreExqVXlOek01T0NKZCIsImV4cCI6IjIwMjMtMDUtMTlUMDU6NTk6NTEuNTI3WiIsInB1ciI6ImNvb2tpZS5yZW1lbWJlcl91c2VyX3Rva2VuIn19--6e4d0e90a73dae9c6c4de73c96594d3112f0cb5a; _devzone_session=c3f0c67e57d0c1dc8b76c908a47deee2; SSESS2088448faf607a381892ca97487fa4c7=OgiRpvCKlv11kRU4V4mjNQk0e9SGrua9nSbVEEuLpRU; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+05+2023+01%3A08%3A50+GMT-0600+(Mountain+Daylight+Time)&version=6.23.0&hosts=&consentId=2594bb82-8cee-4b85-b314-a83e40044968&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0004%3A0%2CC0003%3A0&AwaitingReconsent=false; mbox=PC#94bacd6001d54eec8f98820bb1a81072.35_0#1746515331|session#05995f980d7c4749a90c107ac01baaba#1683272391' \
  -H 'dnt: 1' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36' \
  --compressed \
  -L --output cudnn-local-repo-rhel7-8.9.0.131-1.0-1.x86_64.rpm

sudo rpm -i cudnn-local-repo-rhel7-8.9.0.131-1.0-1.x86_64.rpm && 
sudo yum install libcudnn8-8.9.0.131-1.cuda12.1 -y &&
sudo yum install libcudnn8-devel-8.9.0.131-1.cuda12.1 -y
(optional) sudo yum install libcudnn8-samples-8.9.0.131-1.cuda12.1 -y

wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda-repo-fedora37-12-1-local-12.1.1_530.30.02-1.x86_64.rpm &&
sudo rpm -i cuda-repo-fedora37-12-1-local-12.1.1_530.30.02-1.x86_64.rpm &&
sudo dnf clean all &&
sudo dnf -y module install nvidia-driver:latest-dkms &&
sudo dnf -y install cuda 

export PATH=/usr/local/cuda-12.1/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
cat /proc/driver/nvidia/version
??? 
# export LD_LIBRARY_PATH=/usr/local/cuda-12.1/targets/x86_64-linux/lib/${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}


#
# (WINDW) .\env\Scripts\activate


# JAX
sudo python -m pip install --upgrade "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
sudo python -m pip install git+https://github.com/sanchit-gandhi/whisper-jax.git
sudo vim jaxIt.py
# !!! ffmpeg required









# TRASH

cd /home/ssm-user
curl 'https://developer.nvidia.com/downloads/compute/cudnn/secure/8.9.0/local_installers/12.x/cudnn-linux-x86_64-8.9.0.131_cuda12-archive.tar.xz/' \
  -H 'cookie: AMCV_F207D74D549850760A4C98C6%40AdobeOrg=1176715910%7CMCMID%7C71794017538113168927256794386408995986%7CMCAID%7CNONE%7CvVersion%7C5.4.0; at_check=true; nvweb_A=3a20aa19-c4d1-4220-aa0c-4e3417062d0d; nv_country_code=US; nvidiaCart={"cart":[],"lastAction":null}; s_fid=3A0A7C8FDD401624-389B99CDF8EF59F0; SESSls=gseo; bm_mi=C7CC7BFF1ECC6EF6518B96F2EE66117E~YAAQFpA6F+FGFOeHAQAAn75i6hNpK/yAkJzhbPfAbzjqytEgjhoV1+0UTPRULTZs+P0kxOEdtp6o1pYlZSXrAUVzw/7UhDtfyc+WBS1CpBIYes9qHColXFPYHymMHwZ0Mloe1k+qs7jQ3V8cJJsczoD/N1FJmtOCBZvSLz6bui/ZXsHT8raXssYmCqZEGlFixlbMByN2x+GX1Sizg8DaYS1NBa2KGBjVBXgaBrWiq6jJfzuB8jmrxMXYf5idL20br1jXbAe0rmKJLsInqtYiFcX+JHxNDqsTBKHHAP/Uot0WrwA/pF7q0DM1F1UB54+mXjjRph1bssDvM9x7VlFJ~1; bm_sv=BB51062C31820D9D06E15D0D52E7B758~YAAQFpA6F+JGFOeHAQAAn75i6hPtwNOgRxcHhFgI/OSoyDsVPjPcbZpJ188/XzMT4lhZ0GF54zJLXORgeRbFh+DfM3jPTeVfkxRa03xmx0PNcke0ugBJgo8u81IEGqsZMkFDTpDfAQMwfyW6DjDJFXX6rWcSFxGkQ1dhNizojkNghYQCGAoox+ieR+otp6Mc1v6H8J1PoO2dzu3nG60PwpfOkoJMTSryX35TCkMvSwG7XrO8xVFMgaPthR8dIcxc~1; ak_bmsc=0B77C2EFB90EC0E8E8D827C6C04FF276~000000000000000000000000000000~YAAQC5A6F8bq5uaHAQAAFvB26hOJFadXAz9wBhyoN4EBX80GAVsuZOq2RCKGdQXRen4f2PSItAK8sHtkR63KSwqRByLv3drkoI2Za9WLzwclfu9hB/FiRkbb5oWTppf9+VOeaAgIQ3aO3LjgR5ixNc60U2FIqT7azuXVyeAJw15BPmyANkxqkkAdadWQ7D95zciP47b/bjMC3sIaN/ibk5ieX2SoH35/AVnGWuoAsYtj7IdK/3Tq5XhW3YMKXT1+0oLyuwzqpZa0gVui57S1OgcmYnfox3usiyc7cSiaGzCqHNBoBRfPFKk8oC+wl5c7Tg/MLt74OqHf7yFOJZjtCNzJCfWKHNMphDQ0hGkaA0/mDkm1Wwa+8J0zPy6VXFgDn/TgmovUQhteIO+ZtNb9Hc8fd8ZntLsU12saE+E4jrOZFuEY+XqYx2a63JtT2rEhZuw=; SESSlsd=https%3A%2F%2Fwww.google.com%2F; SESSloginhint=cbrodski%40gmail.com; SESSauthn=1; SESSpg=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJTX3h3ME9ic0NnTDlyazRkMFc4MjNrcE00a1ZUV2NaSDQ4ai11dUh5N1drIiwicHJvZ3JhbV9pZHMiOltdLCJleHAiOjE2ODMyNjgxOTF9.cYJR6s5hoGszFAu8tLSrT-hL_Y0ZAmqf4kDtw_ZY2Wo; SESSdocs=eyJhbGciOiJIUzI1NiJ9.eyJwcm9ncmFtX2lkcyI6Wzg3ODQzMV0sImlhdCI6MTY4MzI2NjM5MSwiZXhwIjoxNjgzMjY5OTkxfQ.JJOHqq7X5o5IZHgQGw9BykN4v5ZNDWgNBmuxWd1jITA; nvweb_E=Ng0muRbpGfwOlHdK11fODOxuBWW-xjsvDS9pwvBA6M6BTDMUS2X5Py3WvbzbBWIxaalcbe9oUzfKUzzkHOX7Yg; nvweb_S=77SfVgBdKv2IUdfq0Ta6rsUNgJFeD5eXW26lD3BmW3nRBjQUseguZchvA_2fylO8eCa4bSe4HtAdtU3-vA747Q; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3pOak00TlRBd1hTd2laWEJhUlVNMWNHTXRjM2g0TFY5WFdWRm1OM1FpTENJeE5qZ3pNalkyTXpreExqVXlOek01T0NKZCIsImV4cCI6IjIwMjMtMDUtMTlUMDU6NTk6NTEuNTI3WiIsInB1ciI6ImNvb2tpZS5yZW1lbWJlcl91c2VyX3Rva2VuIn19--6e4d0e90a73dae9c6c4de73c96594d3112f0cb5a; _devzone_session=c3f0c67e57d0c1dc8b76c908a47deee2; SSESS2088448faf607a381892ca97487fa4c7=OgiRpvCKlv11kRU4V4mjNQk0e9SGrua9nSbVEEuLpRU; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+05+2023+00%3A01%3A07+GMT-0600+(Mountain+Daylight+Time)&version=6.23.0&hosts=&consentId=2594bb82-8cee-4b85-b314-a83e40044968&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0004%3A0%2CC0003%3A0&AwaitingReconsent=false; mbox=PC#94bacd6001d54eec8f98820bb1a81072.35_0#1746511268|session#dc9cc785a4b248b39e9b67bb7611f36f#1683268328' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36' \
  --compressed \
  -L --output cudnn-linux-x86_64-8.9.0.131_cuda12-archive.tar.xz

tar -xvf cudnn-linux-x86_64-8.9.0.131_cuda12-archive.tar.xz
sudo cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include &&
sudo cp -P cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64  &&
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*

'''

# wget https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/testz/BarbaraWalters.mp3