const configs = require("../configs");
const channelHelper = require("./channelHelper");
const DatabaseSingleton = require("./helpers/DatabaseSingleton");
const databaseSingleton = require("./helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");
// https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json


// path = /channel/lolgeranimo
exports.channel = async (req, res) => {    
    // Get all channels
    const endpoint = configs.S3_BUCKET + configs.S3_EACH_CHANNEL_JSON + req.params.name + ".json";   //  https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/each-channel/lolgeranimo.json
    const response = await fetch(endpoint); // mocks/completed_captions_list.py
    let scrapped_data_s3 = {}
    if (!response.ok) {
        //  throw new Error('HTTP error ' + response.status);
    } 
    else {
        scrapped_data_s3 = await response.json()
    }
    

    const endpoint2 = configs.S3_BUCKET + configs.S3_CUSTOM_METADATA_KEYBASE + req.params.name + "/custom-metadata.json";  //     /channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json    
    const res2 = await fetch(endpoint2); // mocks/completed_captions_list.py
    let custom_metadata = {}
    if (!res2.ok) {
        //  throw new Error('HTTP error ' + res2.status);
    } 
    else {
        custom_metadata = await res2.json();
    }
    

    let transcript_s3_vtt;
    let transcript_s3_json;
    let transcript_s3_txt;
    let vod;
    // let profilePic = channelHelper.getProfilePic(req, custom_metadata);
    let profilePic = "";
    console.log("-----------------------------------------------------")
    // console.log("-----------------------------------------------------")
    // console.log("-----------------------------------------------------")
    // console.log("scrapped_data_s3")
    // console.log(scrapped_data_s3)
    // console.log("=====================================================")
    // console.log("=====================================================")
    // console.log("=====================================================")
    // console.log("custom_metadata")
    // console.log(custom_metadata)

    // if (req.params.id != null) {
    //     vod = scrapped_data_s3.filter( vod => vod.id == req.params.id)[0]
    //     console.log("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    //     console.log("vod")
    //     console.log(vod)
    //     if (vod == null) {
    //         res.status(404)
    //         res.render('404', {
    //             msg: "😢 😞 😟 😭 😿"
    //         })
    //         return
    //     }
    //     let lastPeriodIdx = vod?.link_s3.lastIndexOf('.');
    //     if (lastPeriodIdx !== -1) {
    //         const tempName = vod.link_s3.substring(0, lastPeriodIdx);
    //         transcript_s3_vtt = tempName + ".vtt"                
    //         transcript_s3_json = tempName + ".json"
    //         transcript_s3_txt = tempName + ".txt"
    //     } 
    // }

    //  ***************************************
    //  CHANNEL
    //  ***************************************
    if (req.params.id == null) {
        // let completedVods = await channelHelper.getVodsCompleted(req.params.name)
        let completedVods = await channelHelper.getVodsCompleted(req.params.name)
        let db = new DatabaseSingleton
        let [resultsVods, fields1] = await db.getVods(req.params.name)
        let [resultsChan, fields2] = await db.getChannel(req.params.name)
        let vods = resultsVods.map( x => new Vod(x))
        let channels = resultsChan.map( x => new Channel(x))
        console.log("vods:", vods)
        console.log("channels:", channels)
        if (channels.length < 1) {
            console.error("BAD QUERY FOR CHANNELS! OR VODS")
            console.log(channels)
        }
        // const [[resultsVods,fields1], [resultsChan,fields2]] = await Promise.all([promiseVods, promiseChan]);

        res.setHeader('Cache-Control', 'private, max-age=3600');
        res.render("../views/channel", { // ---> /channel/lolgeranimo
            "title" : req.params.name,
            "path" : req.path,
            "scrapped_data_s3": scrapped_data_s3,
            "custom_metadata": custom_metadata,
            "completedVods": completedVods,
            "profilePic": profilePic,
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
        let [resultsVods, fields1] = await db.get1Vod(req.params.id)
        let vods = resultsVods.map( x => new Vod(x))
        let channels = resultsChan.map( x => new Channel(x))
        console.log("TRANSCRIPT - VOD") 
        console.log(channels) 
        console.log(vods) 
        if (channels.length < 1 || vods.length) {
            console.error("BAD QUERY FOR CHANNELS! OR VODS")
            console.log(channels)
        }

        let response = await fetch(transcript_s3_json);
        if (!response.ok) {
             throw new Error('HTTP error ' + response.status);
        }
        let transcript_json = await response.json()
        
        res.render("../views/vod", { // ---> /channel/lolgeranimo
            "channel": vod.channel,
            "transcript_json": transcript_json.segments,
            "vod": vod,
            "vod2": custom_metadata[req.params.id],
            "transcript_s3_vtt": transcript_s3_vtt,
            "transcript_s3_json": transcript_s3_json,
            "transcript_s3_txt": transcript_s3_txt,
            "profilePic": profilePic
        })
        return
    }

    //  ***************************************
    //  CHANNEL - VOD - WORDTREE
    //  ***************************************
    if (req.params.id != null && req.path.includes("/wordtree")) {
        let sentence_arr = await channelHelper.prepWordTree(transcript_s3_txt)
        res.render("../views/wordtree", {
            "sentence_arr": sentence_arr,
            "channel": vod.channel,
            "vod": vod,
            "vod2": custom_metadata[req.params.id],
            "profilePic":profilePic
        })
        return
    }
    //  ***************************************
    //  CHANNEL - VOD - ANALYSIS
    //  ***************************************
    if (req.params.id != null && req.path.includes("/analysis")) {
        let analysisObj = await channelHelper.getAnalysis(transcript_s3_txt)
        res.render("../views/analysis", { // ---> /channel/lolgeranimo
            "channel": vod.channel,
            "vod": vod,
            "vod2": custom_metadata[req.params.id],
            "wordcloud": analysisObj.wordcloudSvg.outerHTML,
            "freqWordPlot": analysisObj.freqWordPlot.outerHTML,
            "badWordPlot": analysisObj.badWordPlot.outerHTML,
            "word_counter": analysisObj.word_counter,
            "bad_words_counter": analysisObj.bad_words_counter,
            "profilePic": profilePic
        })
        return
    }

}

