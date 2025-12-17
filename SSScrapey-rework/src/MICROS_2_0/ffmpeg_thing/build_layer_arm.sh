#https://aws.amazon.com/blogs/media/processing-user-generated-content-using-aws-lambda-and-ffmpeg/

cd build_arm

wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz

wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz.md5

md5sum -c ffmpeg-release-arm64-static.tar.xz.md5

tar xvf ffmpeg-release-arm64-static.tar.xz

mkdir -p ffmpegX/bin

cp ffmpeg-7.0.2-arm64-static/ffmpeg   ffmpegX/bin/
#cp ffmpeg-7.0.2-arm64-static/ffprobe  ffmpeg/bin/

cd ffmpegX
zip -r ../ffmpeg.zip .



