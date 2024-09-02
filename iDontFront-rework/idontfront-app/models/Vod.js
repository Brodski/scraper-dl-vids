class Vod {
    constructor({Id = '', ChannelNameId = '', Title = '', Duration = '', DurationString = '', ViewCount = '', WebpageUrl = '', TranscriptStatus = '', Priority = '', Thumbnail = '', TodoDate = '', S3Audio = '', Model = '', DownloadDate = '', StreamDate = '', TranscribeDate = '', DisplayName = '', Language = '', Logo = '', CurrentRank = '', TwitchUrl = '', S3CaptionFiles = null, S3Thumbnails = null, }) {
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
        this.transcribeDate = TranscribeDate;
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
        if (!key) {
            console.log(`File ext ${ext} not found :(`)
        }
        return key
    }
}

module.exports = Vod;