class Channel {
    constructor({DisplayName = '', NameId = '', Language = '', Logo = '', TwitchUrl = '', CurrentRank = 999, ViewMinutes = '', StreamedMinutes = '', MaxViewers = '', AvgViewers = '', Followers = '', FollowersGained = '', Partner = '', Affiliate = '', Mature = '', PreviousViewMinutes = '', PreviousStreamedMinutes = '', PreviousMaxViewers = '', PreviousAvgViewers = '', PreviousFollowerGain = '', DaysMeasured = '', CompletedCount = '', BroadcastCount = '', TotalCompletedCount = ''}) {
        this.currentRank = CurrentRank;
        this.displayName = DisplayName;
        this.nameId = NameId;
        this.language = Language;
        this.logo = Logo;
        this.twitchUrl = TwitchUrl;

        this.viewMinutes = ViewMinutes
        this.streamedMinutes = StreamedMinutes
        this.maxViewers = MaxViewers
        this.avgViewers = AvgViewers
        this.followers = Followers
        this.followersGained = FollowersGained
        this.partner = Partner
        this.affiliate = Affiliate
        this.mature = Mature
        this.previousViewMinutes = PreviousViewMinutes
        this.previousStreamedMinutes = PreviousStreamedMinutes
        this.previousMaxViewers = PreviousMaxViewers
        this.previousAvgViewers = PreviousAvgViewers
        this.previousFollowerGain = PreviousFollowerGain
        this.daysMeasured = DaysMeasured
        this.completedCount = CompletedCount
        this.broadcastCount = BroadcastCount
        this.totalCompletedCount = TotalCompletedCount
    }
}

module.exports = Channel;
