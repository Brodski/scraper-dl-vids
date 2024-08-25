
const DatabaseSingleton = require("../controllers/helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");
const channelHelper = require("../controllers/channelHelper");

async function getWordtreePage(req, res) {
    let [sentence_arr, most_freq_word] = [null, null]
    let db = new DatabaseSingleton();
    let [resultsChan, fields2] = await db.getChannel(req.params.name)
    let [resultsVods, fields1] = await db.getVodById(req.params.id)
    let vods = resultsVods.map( x => new Vod(x))
    let channels = resultsChan.map( x => new Channel(x))
    if (vods.length == 0 || channels.length == 0) {
        console.error("BAD QUERY FOR CHANNELS! OR VODS (wordtree)")
        return "failed_helper"
    }
    txtKey = process.env.BUCKET_DOMAIN + "/" + vods[0].getS3TxtKey();

    // Process important data
    try {
        [sentence_arr, most_freq_word] = await channelHelper.prepWordTree(txtKey)
    } catch (e) {
        return "failed_helper"
    }

    res.render("../views/wordtree", {
        "sentence_arr": sentence_arr,
        "most_freq_word": most_freq_word,
        "vod": vods[0],
        "channel": channels[0]
    })
    return
}
module.exports = { getWordtreePage }