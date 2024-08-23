
const DatabaseSingleton = require("../controllers/helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");

exports.sitemap = async (req, res) => {
    console.log("GETTING SITEMAP: ", req.path)
    let db = new DatabaseSingleton;
    let [resultsVods, fields1] = await db.getAllTranscribedVods()
    let channelsList = await db.getChannelsForHomepage()
    let vods = resultsVods.map( x => new Vod(x))
    console.log("channelsList", channelsList)
    // let channels = resultsChannels.map( x => new Channel(x))
    res.type("application/xml")
    res.render("../views/sitemap", {
        "vods": vods,
        "channels": channelsList
    }) 
}