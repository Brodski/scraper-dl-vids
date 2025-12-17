#https://aws.amazon.com/blogs/media/processing-user-generated-content-using-aws-lambda-and-ffmpeg/

cd build

wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz.md5

md5sum -c ffmpeg-release-amd64-static.tar.xz.md5

tar xvf ffmpeg-release-amd64-static.tar.xz

mkdir -p ffmpeg/bin

cp ffmpeg-7.0.2-amd64-static/ffmpeg   ffmpeg/bin/
#cp ffmpeg-7.0.2-amd64-static/ffprobe  ffmpeg/bin/


cd ffmpeg
zip -r ../ffmpeg.zip .
