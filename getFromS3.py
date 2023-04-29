import requests
import time

start_time = time.time()


url = 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/testz/BarbaraWalters.mp3'
response = requests.get(url)
print("got response:" )
print(response)
print(response.status_code)
print()
print("response.content:")
with open('s3333.mp3', 'wb') as f:
    f.write(response.content)

run_time = time.time() - start_time
print("run_time=" + str(run_time))
response_size_bytes = len(response.content)
print("size = " + str(response_size_bytes))
# Git
# sudo yum update
# sudo dnf install git-all
#
# Python
# sudo yum groupinstall "Development Tools" -y
# sudo yum install openssl-devel libffi-devel bzip2-devel -y
# sudo yum install openssl-devel libffi-devel bzip2-devel zlib-devel sqlite-devel readline-devel xz-devel wget -y
# !
# cd /home/ssm-user
# sudo curl -O https://www.python.org/ftp/python/3.10.10/Python-3.10.10.tgz
# sudo tar -xzf Python-3.10.10.tgz
# cd Python-3.10.10/
# sudo  ./configure --enable-optimizations --with-ensurepip=install
# sudo make altinstall
# sudo ln -s /usr/local/bin/python3.10 /usr/local/bin/python
# cd /home/ssm-user
# sudo rm Python-3.10.10.tgz
# Pip 
# ????????????????????????????
# cd /home/ssm-user
# sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# sudo python get-pip.py pip==23.0.1
# pip --version
# sudo rm get-pip.py
#
# Proj
# sudo git clone https://github.com/Brodski/scraper-dl-vids.git
# sudo python -m pip install virtualenv
# sudo python -m virtualenv venv
# (LINUX) source venv/bin/activate
# (WINDW) .\env\Scripts\activate
# (testin) python -m pip install requests
# pip install -r requirements.txt
# 
# sudo pip install requests