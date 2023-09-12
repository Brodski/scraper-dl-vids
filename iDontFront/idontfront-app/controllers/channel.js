const configs = require("../configs")
// const { add, subtract } = require('../server-scripts/dates');

// https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json


// path = /channel/lolgeranimo
exports.channel = async (req, res) => {
    
    const endpoint = configs.S3_BUCKET + configs.S3_EACH_CHANNEL_JSON + req.params.name + ".json";   //  https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/each-channel/lolgeranimo.json
    const response = await fetch(endpoint); // mocks/completed_captions_list.py
    if (!response.ok) {
         throw new Error('HTTP error ' + response.status);
    }
    let scrapped_data_s3 = await response.json()
    const endpoint2 = configs.S3_BUCKET + configs.S3_CUSTOM_METADATA_KEYBASE + req.params.name + "/custom-metadata.json"; 
    //     /channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json
    const res2 = await fetch(endpoint2); // mocks/completed_captions_list.py
    console.log("endpoint2", endpoint2);
    // timestamp = date I ran my scraper
    // epoch = date of upload
    if (!res2.ok) {
         throw new Error('HTTP error ' + res2.status);
    }
    let custom_metadata = await res2.json();

    //  ***************************************
    //  ***************************************
    //  ***************************************
    //  ***************************************
    //  CHANNEL PATH
    // 
    // 
    // http://localhost:3333/channel/lolgeranimo
    if (req.params.id == null) {
        res.render("../views/channel", { // ---> /channel/lolgeranimo
            "title" : req.params.name,
            "path" : req.path,
            "scrapped_data_s3": scrapped_data_s3,
            "custom_metadata": custom_metadata
        })
    }


    //  ***************************************
    //  ***************************************
    //  ***************************************
    //  ***************************************
    //  VOD PATH
    // 
    // 
    if (req.params.id != null) {
        let vod = scrapped_data_s3.filter( vod => vod.id == req.params.id)[0]
        if (vod == null) {
            res.status(404).render('404')
        }
        let transcript_s3_vtt, transcript_s3_json;

        let lastPeriodIdx = vod?.link_s3.lastIndexOf('.');
        if (lastPeriodIdx !== -1) {
            const tempName = vod.link_s3.substring(0, lastPeriodIdx);
            transcript_s3_vtt = tempName + ".vtt"                
            transcript_s3_json = tempName + ".json"
            transcript_s3_txt = tempName + ".txt"
        } 

        let endpoint = transcript_s3_json;
        let response = await fetch(endpoint);
        console.log("endpoint transcript_s3_json=", endpoint);
        if (!response.ok) {
             throw new Error('HTTP error ' + response.status);
        }
        let transcript_json = await response.json()
        vod.channel;
        vod.link_s3;
        vod.title;
        vod.id;
        res.render("../views/vod", { // ---> /channel/lolgeranimo
            "channel": vod.channel,
            "transcript_json": transcript_json.segments,
            "vod": vod,
            "vod2": custom_metadata[req.params.id],
            "transcript_s3_vtt": transcript_s3_vtt,                            
            "transcript_s3_json": transcript_s3_json,                        
            "transcript_s3_txt": transcript_s3_txt                            
        })
    }
}

