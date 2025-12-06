cd "/mnt/c/Users/BrodskiTheGreat/Desktop/desktop/Code/scraper-dl-vids/MICROS_2_0/ffmpeg_thing"
mkdir -p build_python/python/lib/python3.14/
cp -r venv/Lib/site-packages build_python/python/lib/python3.14/.
cd build_python
zip -r my_layer.zip python

# pip install mysqlclient
