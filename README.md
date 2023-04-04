NEED PYTHON 3.10 B/C OF AI-WHISPER

Start:
$ venv\Scripts\activate
$ deactivate
$ python .\scrape.py
$ python .\whisperGogogo.py


- Apparently "*python -m* pip install -r requirements.txt" is the new meta
- (python -m pip executes pip using the Python interpreter you specified as python. So /usr/bin/python3.7 -m pip means you are executing pip for your interpreter located at /usr/bin/python3.7.)

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
$ choco install ffmpeg

(recall)
pip install -r requirements.txt
pip freeze > requirements.txt
python -m virtualenv venv
