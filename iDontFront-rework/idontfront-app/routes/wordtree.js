
const DatabaseSingleton = require("../controllers/helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");
const channelHelper = require("../controllers/channelHelper");

async function getWordtreePage(req, res) {
    let db = new DatabaseSingleton();
    let [resultsChan, fields2] = await db.getChannel(req.params.name)
    let [resultsVods, fields1] = await db.getVodById(req.params.id)
    let vods = resultsVods.map( x => new Vod(x))
    let channels = resultsChan.map( x => new Channel(x))
    console.log(vods[0].getS3TxtKey())
    console.log( process.env.BUCKET_DOMAIN + "/" + vods[0].getS3TxtKey())
    txtKey = process.env.BUCKET_DOMAIN + "/" + vods[0].getS3TxtKey();

    // let sentence_arr = await channelHelper.prepWordTree(transcript_s3_txt)
    let sentence_arr = await channelHelper.prepWordTree(txtKey)
    res.render("../views/wordtree", {
        "sentence_arr": sentence_arr,
        "vod": vods[0],
        "channel": channels[0]
    })
    return
}
module.exports = { getWordtreePage }