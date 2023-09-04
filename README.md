# ! Work in progress !  

### auto-vast-runner  
Runs a daily lambda to start up a audio2Text via Vasti AI
$ terraform apply -var "VAST_API_KEY=11111111111111111111111111111111"   
Dockerfile_SSScrapey -> ran nightly in AWS. Containerizes SSScrapey dir. 

NEED PYTHON 3.10 B/C OF AI-WHISPER  

Start:  
$ venv\Scripts\activate  
$ deactivate  
$ python .\scrape.py  
$ python .\whisperGogogo.py  
  
  
- Apparently "*python -m* pip install -r requirements.txt" is the new meta  
- (python -m pip executes pip using the Python interpreter you specified as python. So /usr/bin/python3.7 -m pip means you are excuting pip for your interpreter located at /usr/bin/python3.7.)  
  
(getting started)  
$ pip install virtualenv  
$ python -m virtualenv venv  

$ .\venv\Scripts\activate  
$ python -m pip install webdriver-manager    
$ python -m pip install beautifulsoup4    
$ python -m pip install yt_dlp   
$ python -m pip install selenium  
$ python -m pip install Flask  
$ python -m pip install -U openai-whisper  
$ python -m pip install flask[async]  
$ python -m pip install boto3  
$ python -m pip install langcodes 
$ python -m pip install language-data
### At some point (prob ai whisper) we downloaded the CPU only version (__version__ = '2.0.0+cpu') found at "\scraper-dl-vids\venv\Lib\site-packages\torch\version.py"  
$ python -m pip uninstall torch  
$ python -m pip cache purge  
$ python -m pip install torch -f https://download.pytorch.org/whl/torch_stable.html  
$ python -m pip install faster_whisper
$ choco install ffmpeg  
  
(recall)  
pip install -r requirements.txt  
pip freeze > requirements.txt  
python -m virtualenv venv  
  
    
ssh root@104.156.226.154 -i "C:\Users\BrodskiTheGreat\Desktop\desktop\Code\vult-ssh"



==========================================
#  AWS

TODO - https://registry.terraform.io/modules/cn-terraform/ecs-fargate-scheduled-task/aws/latest 


Create an AWS Fargate Cluster
Create an AWS Fargate Cluster
Create an AWS Fargate Cluster
Create an AWS Fargate Cluster
https://www.youtube.com/watch?v=WsvuIxaCQGg
https://www.youtube.com/watch?v=WsvuIxaCQGg
https://www.youtube.com/watch?v=WsvuIxaCQGg
https://www.youtube.com/watch?v=WsvuIxaCQGg
https://www.youtube.com/watch?v=WsvuIxaCQGg

LOGS
LOGS
LOGS
LOGS
https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups



=====================
ssscrapey
pip install boto3
pip install python-dotenv
pip install boto3
pip install beautifulsoup4
pip install selenium
pip install webdriver-manager==3.8.5

// apt-get install chromium-driver -y
// pip install ffmpeg
// pip install ffprobe
apt-get install ffmpeg
apt install firefox


???
pip isntall flask