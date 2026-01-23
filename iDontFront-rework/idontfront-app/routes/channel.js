const Vod = require("../models/Vod");
const Channel = require("../models/Channel");
const DatabaseSingleton = require("../controllers/helpers/DatabaseSingleton");

async function getChannelPage(req, res) {
    
    console.log("GETTING CHANNEL: ", req.params.name)
    let db = new DatabaseSingleton
    let [resultsVods, fields1] = await db.getVods(req.params.name)
    let [resultsChan, fields2] = await db.getChannel(req.params.name)
    let vods = resultsVods.map( x => new Vod(x))
    let channels = resultsChan.map( x => new Channel(x))
    if (channels.length < 1) {
        console.error("BAD QUERY FOR CHANNELS! OR VODS (a)")
        console.log(channels)
        return "failed_helper"
    }

    // res.set('Cache-Control', `${res.getHeader("cache-control")}, s-maxage=3600`); // 1 hours
    res.render("../views/channel", { 
        "title" : req.params.name,
        "path" : req.path,
        "vods": vods,
        "channel": channels[0],
    })
    return "success"
}


module.exports = { 
    getChannelPage
}
