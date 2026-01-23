
const DatabaseSingleton = require("../controllers/helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");

exports.sitemap = async (req, res) => {
    let db = new DatabaseSingleton;
    let [resultsVods, fields1] = await db.getAllTranscribedVods()
    let [channelsStreamed, channelsZeroStreamed] = await db.getChannelsForHomepage()
    let channelsList = [...channelsStreamed, ...channelsZeroStreamed]
    let vods = resultsVods.map( x => new Vod(x))
    res.type("application/xml")
    // res.set('Cache-Control', `${res.getHeader("cache-control")}, s-maxage=3600`); // 1 hours
    res.render("../views/sitemap", {
        "vods": vods,
        "channels": channelsList
    }) 
}