class Vod {
    constructor({Id = '', ChannelNameId = '', Title = '', Duration = '', DurationString = '', ViewCount = '', WebpageUrl = '', TranscriptStatus = '', Priority = '', Thumbnail = '', TodoDate = '', S3Audio = '', Model = '', DownloadDate = '', StreamDate = '', DisplayName = '', Language = '', Logo = '', CurrentRank = '', TwitchUrl = '', S3CaptionFiles = null, S3Thumbnails = null}) {
        this.id = Id;
        this.channelNameId = ChannelNameId;
        this.title = Title;
        this.duration = Duration;
        this.durationString = DurationString;
        this.viewCount = ViewCount;
        this.webpageUrl = WebpageUrl;
        this.transcriptStatus = TranscriptStatus;
        this.priority = Priority;
        this.thumbnail = Thumbnail;
        this.todoDate = TodoDate;
        this.s3Audio = S3Audio;
        this.model = Model;
        this.downloadDate = DownloadDate; // TODO MAKE THIS DATETIME OBJECT IN MYSQL
        this.streamDate = StreamDate;
        // joined channels table

        this.channelDisplayName = DisplayName
        this.channelLanguage = Language
        this.channelLogo = Logo
        this.channelCurrentRank = CurrentRank
        this.channelTwitchUrl = TwitchUrl
        this.s3CaptionFiles = S3CaptionFiles
        this.s3Thumbnails = S3Thumbnails
    }
    getS3TranscriptKey() {        
        return this._getS3Key(".json")
    }
    getS3VttKey() {        
        return this._getS3Key(".vtt")
    }
    getS3TxtKey() {        
        return this._getS3Key(".txt")
    }
    _getS3Key(ext) {
        const key = this.s3CaptionFiles?.find(file => file.endsWith(ext));
        console.log("this.s3CaptionFiles")
        console.log(this.s3CaptionFiles)
        if (!key) {
            console.log(`File ext ${ext} not found :(`)
        }
        return key
    }
}

module.exports = Vod;
//   channels/vod-audio/kaicenat/2143646862/100%2B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.opus

// ["channels/vod-audio/kaicenat/2143646862/100%25252B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.json", "channels/vod-audio/kaicenat/2143646862/100%25252B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.vtt", "channels/vod-audio/kaicenat/2143646862/100%25252B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.txt", "channels/vod-audio/kaicenat/2143646862/100%25252B_HR_STREAM_ELDEN_RING_CLICK_HERE_GAMER_BIGGEST_DWARF_ELITE_PRAY_4_ME-v2143646862.srt"]
//               
// https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com