class Channel {
    constructor({DisplayName = '', NameId = '', Language = '', Logo = '', TwitchUrl = '', CurrentRank = 999}) {
        this.currentRank = CurrentRank;
        this.displayName = DisplayName;
        this.nameId = NameId;
        this.language = Language;
        this.logo = Logo;
        this.twitchUrl = TwitchUrl;
    }
}

module.exports = Channel;
