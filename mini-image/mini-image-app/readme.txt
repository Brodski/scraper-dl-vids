#
# TO make this work in lambda we must do this:
#
# make lambda arm64
npm install @img/sharp-linux-arm64 --force
npm install @img/sharp-libvips-linux-arm64 --force
npm install --os=linux --cpu=arm64 --include=optional sharp --force