
const DatabaseSingleton = require("../controllers/helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");

async function getVodPage(req, res) {
    let db = new DatabaseSingleton();
    let [resultsChan, fields2] = await db.getChannel(req.params.name)
    let [resultsVods, fields1] = await db.getVodById(req.params.id)
    let vods = resultsVods.map( x => new Vod(x))
    let channels = resultsChan.map( x => new Channel(x))
    if (channels.length != 1 || vods.length != 1) {
        console.error("BAD QUERY FOR CHANNELS! OR VODS (b)")
        console.log(channels)
    }
    
    // let transcript_s3_key = encodeURI(vods[0].getS3TranscriptKey());
    let transcript_s3_key = vods[0].getS3TranscriptKey();
    let url = process.env.BUCKET_DOMAIN + "/" + transcript_s3_key
    let response = await fetch(url);
    console.log(" process.env.BUCKET_DOMAIN:",  process.env.BUCKET_DOMAIN)
    console.log(" process.env.BUCKET_DOMAIN:",  process.env.BUCKET_DOMAIN)
    console.log(" url:",  url)
    console.log(" url:",  url)
    if (!response.ok) {
        console.error("Failed HTTT-Get: ", url);
        throw new Error('HTTP error ' + response.status);
    }
    let transcript_json = await response.json()
    vttKey = process.env.BUCKET_DOMAIN + "/" + vods[0].getS3VttKey();
    jsonKey = process.env.BUCKET_DOMAIN + "/" + vods[0].getS3TranscriptKey();
    txtKey = process.env.BUCKET_DOMAIN + "/" + vods[0].getS3TxtKey();
    console.log("TRANSCRIPT - VOD: ", vods[0]?.id, vods[0]?.title) 
    res.render("../views/vod", { // ---> /channel/lolgeranimo
        "transcript_json": transcript_json.segments,
        "transcript_s3_vtt":  encodeURI(vttKey),
        "transcript_s3_json": encodeURI(jsonKey),
        "transcript_s3_txt":  encodeURI(txtKey),
        "vod": vods[0],
        "channel": channels[0]
    })
    return
}
module.exports = { 
    getVodPage
}