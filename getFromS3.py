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
print(run_time)

# Git
# sudo yum update
# sudo dnf install git-all
#
# Python
# sudo yum groupinstall "Development Tools" -y
# sudo yum install openssl-devel libffi-devel bzip2-devel -y
# sudo curl -O https://www.python.org/ftp/python/3.10.10/Python-3.10.10.tgz
# sudo tar -xzf Python-3.10.10.tgz
# cd Python-3.10.10/
# sudo  ./configure --enable-optimizations --with-ensurepip=install
# sudo make altinstall
# sudo ln -s /usr/local/bin/python3.10 /usr/local/bin/python
#
# Pip 
# ????????????????????????????
# cd /home/helloMe/
# sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# sudo python get-pip.py==22.3.1
# sudo python get-pip.py pip==23.0.1
# pip --version
#
# Proj
# sudo git clone https://github.com/Brodski/scraper-dl-vids.git
# sudo python -m pip install virtualenv
# sudo python -m virtualenv venv
# pip install -r requirements.txt
# 
# sudo pip install requests