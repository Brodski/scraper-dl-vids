const configs = require("../configs");
const channelHelper = require("./channelHelper");
const DatabaseSingleton = require("./helpers/DatabaseSingleton");
// const databaseSingleton = require("./helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");
// https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json


// path = /channel/lolgeranimo
exports.channel = async (req, res) => { 
    let profilePic = "";
    console.log("-----------------------------------------------------")
    //  ***************************************
    //  CHANNEL
    //  ***************************************
    if (req.params.id == null) {
        console.log("GETTING CHANNEL: ", req.params.name)
        // let completedVods = await channelHelper.getVodsCompleted(req.params.name)
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
        // const [[resultsVods,fields1], [resultsChan,fields2]] = await Promise.all([promiseVods, promiseChan]);

        res.setHeader('Cache-Control', 'private, max-age=3600');
        res.render("../views/channel", { 
            "title" : req.params.name,
            "path" : req.path,
            "vods": vods,
            "channel": channels[0],
        })
        return
    }

    //  ***************************************
    //  CHANNEL - VOD 
    //  ***************************************
    if (req.params.id != null && !req.path.includes("/analysis") && !req.path.includes("/wordtree") ) {
        let db = new DatabaseSingleton();
        let [resultsChan, fields2] = await db.getChannel(req.params.name)
        let [resultsVods, fields1] = await db.getVodById(req.params.id)
        let vods = resultsVods.map( x => new Vod(x))
        let channels = resultsChan.map( x => new Channel(x))
        if (channels.length != 1 || vods.length != 1) {
            console.error("BAD QUERY FOR CHANNELS! OR VODS (b)")
            console.log(channels)
        }

        let transcript_s3_key = vods[0].getS3TranscriptKey() 
        console.log(" process.env.BUCKET_DOMAIN:",  process.env.BUCKET_DOMAIN)
        console.log(" process.env.BUCKET_DOMAIN:",  process.env.BUCKET_DOMAIN)
        console.log(" process.env.BUCKET_DOMAIN:",  process.env.BUCKET_DOMAIN)
        let url = process.env.BUCKET_DOMAIN + "/" + transcript_s3_key
        let response = await fetch(url);
        if (!response.ok) {
// https://my-prod-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/tarik/2098078110/SEN_vs._GEN_-_Masters_Madrid_-_Twitter_%2540tarik_MastersCostream-v2098078110.json
 // https://my-dev-bucket-bigger-stronger-faster-richer-than-your-bucket.s3.amazonaws.com/channels/vod-audio/tarik/2098078110/SEN_vs._GEN_-_Masters_Madrid_-_Twitter_%252540tarik_MastersCostream-v2098078110.json
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
            "transcript_s3_vtt":  vttKey,
            "transcript_s3_json": jsonKey,
            "transcript_s3_txt":  txtKey,
            "vod": vods[0],
            "channel": channels[0]
        })
        return
    }

    //  ***************************************
    //  CHANNEL - VOD - WORDTREE
    //  ***************************************
    if (req.params.id != null && req.path.includes("/wordtree")) {
        let db = new DatabaseSingleton();
        let [resultsChan, fields2] = await db.getChannel(req.params.name)
        let [resultsVods, fields1] = await db.getVodById(req.params.id)
        let vods = resultsVods.map( x => new Vod(x))
        let channels = resultsChan.map( x => new Channel(x))
        txtKey = process.env.BUCKET_DOMAIN + "/" + vods[0].getS3TxtKey();

        // let sentence_arr = await channelHelper.prepWordTree(transcript_s3_txt)
        let sentence_arr = await channelHelper.prepWordTree(txtKey)
        res.render("../views/wordtree", {
            "sentence_arr": sentence_arr,
            // "channel": vod.channel,
            // "vod": vod,
            // "vod2": custom_metadata[req.params.id],
            // "profilePic": profilePic,
            "vod": vods[0],
            "channel": channels[0]
        })
        return
    }
    //  ***************************************
    //  CHANNEL - VOD - ANALYSIS
    //  ***************************************
    if (req.params.id != null && req.path.includes("/analysis")) {
        let db = new DatabaseSingleton();
        let [resultsChan, fields2] = await db.getChannel(req.params.name)
        let [resultsVods, fields1] = await db.getVodById(req.params.id)
        let vods = resultsVods.map( x => new Vod(x))
        let channels = resultsChan.map( x => new Channel(x))
        txtKey = process.env.BUCKET_DOMAIN + "/" + vods[0].getS3TxtKey();
        let analysisObj = await channelHelper.getAnalysis(txtKey)
        res.render("../views/analysis", { // ---> /channel/lolgeranimo
            "channel": channels[0],
            "vod": vods[0],

            // "vod2": custom_metadata[req.params.id],
            "wordcloud": analysisObj.wordcloudSvg?.outerHTML,
            "freqWordPlot": analysisObj.freqWordPlot?.outerHTML,
            "badWordPlot": analysisObj.badWordPlot?.outerHTML,
            "word_counter": analysisObj.word_counter,
            "bad_words_counter": analysisObj.bad_words_counter,

            // "profilePic": profilePic
        })
        return
    }

}

