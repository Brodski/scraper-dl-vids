class Vod {
    constructor({Id = '', ChannelNameId = '', Title = '', Duration = '', DurationString = '', ViewCount = '', WebpageUrl = '', TranscriptStatus = '', Priority = '', Thumbnail = '', TodoDate = '', S3Audio = '', Model = '', DownloadDate = '', StreamDate = '', DisplayName = '', Language = '', Logo = '', CurrentRank = '', TwitchUrl = ''}) {
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
    }
}

module.exports = Vod;
