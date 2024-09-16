
const DatabaseSingleton = require("../controllers/helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");
const getLangCode = require("../controllers/helpers/language2Code")

// Lambda can only return a response at max 6MB, we have to trim the content
async function checkSize(transcript_json, counter) {
    let jsonString = JSON.stringify(transcript_json);
    let sizeBytes = Buffer.byteLength(jsonString, 'utf8');
    let sizeMB = sizeBytes / (1024 * 1024);
    let MAX_SIZE_MB = 2.3 // TODO make this smaller, perhaps lower the Memory usage for lambda in terraform $$$. MAX_SIZE_MB = coefficent that does the trick
    if (sizeMB - 0.05 <= MAX_SIZE_MB || counter > 4) { // 0.05 is arbitrary "computer rounding imperfection" fix ... If counter>4 then we risk lambda max response 6MB but prob another error is causing the long looping
        return false
    }
    let scale_down_var = MAX_SIZE_MB / sizeMB

    let segments = transcript_json["segments"]
    let scale_down_var2 = Math.floor(segments.length * scale_down_var)
    let trimmed = segments.slice(0, scale_down_var2)
    transcript_json['segments'] = trimmed // updatd b/c pass by ref
    checkSize(transcript_json, counter + 1) // we run again, to make sure it has ACTUALLY been reduced
    return true
}

async function getVodPage(req, res) {
    let db = new DatabaseSingleton();
    let [resultsChan, fields2] = await db.getChannel(req.params.name)
    let [resultsVods, fields1] = await db.getVodById(req.params.id)
    let vods = resultsVods.map( x => new Vod(x))
    let channels = resultsChan.map( x => new Channel(x))
    if (channels.length != 1 || vods.length != 1) {
        console.error("BAD QUERY FOR CHANNELS! OR VODS (b)")
        console.log(channels)
        return "failed_helper"
    }

    let transcript_s3_key = encodeURI(vods[0].getS3TranscriptKey());
    let url = process.env.BUCKET_DOMAIN + "/" + transcript_s3_key
    let response = await fetch(url);

    if (!response.ok) {
        console.error("Failed HTTP-Get: ", url);
        throw new Error('HTTP error ' + response.status);
    }

    let transcript_json = await response.json()
    vttKey = process.env.BUCKET_DOMAIN + "/" + vods[0].getS3VttKey();
    jsonKey = process.env.BUCKET_DOMAIN + "/" + vods[0].getS3TranscriptKey();
    txtKey = process.env.BUCKET_DOMAIN + "/" + vods[0].getS3TxtKey();
    console.log("TRANSCRIPT - VOD: ", vods[0]?.id, vods[0]?.title) 

    // console.time('check')
    await checkSize(transcript_json, 1)
    // console.timeEnd('check')
    
    // BOOM 👇
    // BOOM 👇
    // BOOM 👇
    res.render("../views/vodGPT", { // ---> /channel/kaicenat
        "transcript_json": transcript_json.segments,
        "transcript_s3_vtt":  encodeURI(vttKey),
        "transcript_s3_json": encodeURI(jsonKey),
        "transcript_s3_txt":  encodeURI(txtKey),
        "lang_code": getLangCode(channels[0]?.language),
        "vod": vods[0],
        "channel": channels[0]
    })
    return
}
module.exports = { 
    getVodPage
}