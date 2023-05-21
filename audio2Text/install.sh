
echo "" 
echo "Python" 
echo "" 
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev -y &&

sudo curl -O https://www.python.org/ftp/python/ /Python-3.10.10.tgz &&
sudo tar -xzf Python-3.10.10.tgz &&
cd Python-3.10.10/ &&
sudo  ./configure --enable-optimizations --with-ensurepip=install &&
make -j $(nproc) &&
sudo make altinstall &&
sudo ln -s /usr/local/bin/python3.10 /usr/local/bin/python &&
cd .. &&
sudo rm Python-3.10.10.tgz


echo ""
echo "PIP"
echo ""
cd /home/titus &&
sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py &&
sudo python get-pip.py pip==23.0.1 &&
pip --version &&
sudo rm get-pip.py &&


echo ""
echo "Project"
echo ""
cd /home/titus &&
sudo apt install git-all -y &&
git clone https://github.com/Brodski/scraper-dl-vids.git &&
cd scraper-dl-vids/ &&
sudo python -m pip install virtualenv &&
sudo python -m virtualenv venv &&
source venv/bin/activate &&
sudo python -m pip install faster-whisper &&
sudo python -m pip install -U openai-whisper &&
??
sudo python -m pip install requests  &&
sudo python -m pip  install torch torchvision torchaudio  &&




# does not fix cuda :/
sudo apt install software-properties-common -y && 
sudo apt update

# NOPE 
wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda-repo-debian11-12-1-local_12.1.1-530.30.02-1_amd64.deb &&
sudo dpkg -i cuda-repo-debian11-12-1-local_12.1.1-530.30.02-1_amd64.deb &&
sudo cp /var/cuda-repo-debian11-12-1-local/cuda-*-keyring.gpg /usr/share/keyrings/ &&
sudo add-apt-repository contrib &&
sudo apt-get update &&
sudo apt-get -y install cuda 



#  DEBIAN
cd /root/ &&
curl 'https://developer.nvidia.com/downloads/compute/cudnn/secure/8.9.1/local_installers/12.x/cudnn-local-repo-debian11-8.9.1.23_1.0-1_amd64.deb/' \
  -H 'cookie: AMCV_F207D74D549850760A4C98C6%40AdobeOrg=1176715910%7CMCMID%7C71794017538113168927256794386408995986%7CMCAID%7CNONE%7CvVersion%7C5.4.0; at_check=true; nvweb_A=3a20aa19-c4d1-4220-aa0c-4e3417062d0d; nv_country_code=US; nvidiaCart={"cart":[],"lastAction":null}; s_fid=3A0A7C8FDD401624-389B99CDF8EF59F0; SESSls=gseo; SESSlsd=https%3A%2F%2Fwww.google.com%2F; SESSloginhint=cbrodski%40gmail.com; SESSauthn=1; nvweb_E=Ng0muRbpGfwOlHdK11fODOxuBWW-xjsvDS9pwvBA6M6BTDMUS2X5Py3WvbzbBWIxaalcbe9oUzfKUzzkHOX7Yg; nvweb_S=77SfVgBdKv2IUdfq0Ta6rsUNgJFeD5eXW26lD3BmW3nRBjQUseguZchvA_2fylO8eCa4bSe4HtAdtU3-vA747Q; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3pOak00TlRBd1hTd2laWEJhUlVNMWNHTXRjM2g0TFY5WFdWRm1OM1FpTENJeE5qZ3pNalkyTXpreExqVXlOek01T0NKZCIsImV4cCI6IjIwMjMtMDUtMTlUMDU6NTk6NTEuNTI3WiIsInB1ciI6ImNvb2tpZS5yZW1lbWJlcl91c2VyX3Rva2VuIn19--6e4d0e90a73dae9c6c4de73c96594d3112f0cb5a; _devzone_session=c3f0c67e57d0c1dc8b76c908a47deee2; SSESS2088448faf607a381892ca97487fa4c7=OgiRpvCKlv11kRU4V4mjNQk0e9SGrua9nSbVEEuLpRU; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+05+2023+01%3A08%3A50+GMT-0600+(Mountain+Daylight+Time)&version=6.23.0&hosts=&consentId=2594bb82-8cee-4b85-b314-a83e40044968&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0004%3A0%2CC0003%3A0&AwaitingReconsent=false; mbox=PC#94bacd6001d54eec8f98820bb1a81072.35_0#1746515331|session#05995f980d7c4749a90c107ac01baaba#1683272391' \
  -H 'dnt: 1' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36' \
  --compressed \
  -L --output cudnn-local-repo-debian11-8.9.1.23_1.0-1_amd64.deb

sudo dpkg -i cudnn-local-repo-debian11-8.9.1.23_1.0-1_amd64.deb
sudo apt install ./cudnn-local-repo-debian11-8.9.1.23_1.0-1_amd64.deb
sudo cp /var/cudnn-local-repo-*/cudnn-local-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get install libcudnn8=8.9.1.23-1+cuda12.1
sudo apt-get install libcudnn8-dev=8.9.1.23-1+cuda12.1
#OPTIONAL 
sudo apt-get install libcudnn8-samples=8.x.x.x-1+cudaX.Y


wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda-repo-debian11-12-1-local_12.1.1-530.30.02-1_amd64.deb &&
sudo dpkg -i cudnn-local-repo-debian11-8.9.1.23_1.0-1_amd64.deb
sudo apt install nvidia-driver -y &&
sudo dnf -y install cuda 

# Vultr
 ssh root@66.135.27.241 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"
 ssh root@140.82.41.231 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"
 ssh root@66.135.27.33 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"

# vast.ai
ssh -p 43687 root@194.44.114.10 -L 8080:localhost:8080 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"
ssh -p 40002 root@75.191.38.75 -L 8080:localhost:8080 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"





 debian-classic
 ssh root@66.135.29.52 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"
 ssh titus@66.135.28.25 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-dvd"

 Get-PSReadLineKeyHandler
 Set-PSReadLineKeyHandler -Chord F4 -ScriptBlock { [Microsoft.PowerShell.PSConsoleReadLine]::ScrollDisplayUp() }

 Debian mirros : https://www.itzgeek.com/how-tos/linux/debian/setup-debian-11-official-repository-in-sources-list-etc-apt-sources-list.html
 set ssh keys in ~/.ssh/authorized_keys