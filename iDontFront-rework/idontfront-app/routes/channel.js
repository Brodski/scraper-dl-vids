
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
    console.log("vods.length:", vods.length)
    console.log("channels.length:", channels.length)
    if (channels.length < 1) {
        console.error("BAD QUERY FOR CHANNELS! OR VODS (a)")
        console.log(channels)
    }

    res.setHeader('Cache-Control', 'private, max-age=3600');
    res.render("../views/channel", { 
        "title" : req.params.name,
        "path" : req.path,
        "vods": vods,
        "channel": channels[0],
    })
    return
}


module.exports = { 
    getChannelPage
}
