const configs = require("../configs")

https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json


// path = /channel/lolgeranimo
exports.channel = async (req, res) => {
    
    const endpoint = configs.S3_BUCKET + configs.S3_EACH_CHANNEL_JSON + req.params.name + ".json";   //  https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/each-channel/lolgeranimo.json
    const response = await fetch(endpoint); // mocks/completed_captions_list.py
    console.log("endpoint", endpoint);
    if (!response.ok) {
         throw new Error('HTTP error ' + response.status);
    }
    let scrapped_data_s3 = await response.json()
    console.log("scrapped_data_s3")
    // console.log(scrapped_data_s3)
    console.log("req.params.id")
    console.log(req.params.id)
        
    // res.locals.overviewLight = overviewLight
    if (req.params.id == null) {
        const endpoint2 = configs.S3_BUCKET + configs.S3_CUSTOM_METADATA_KEYBASE + req.params.name + "/custom-metadata.json"; 
        //     /channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json
        const res2 = await fetch(endpoint2); // mocks/completed_captions_list.py
        console.log("endpoint2", endpoint2);
        if (!res2.ok) {
             throw new Error('HTTP error ' + res2.status);
        }
        let custom_metadata = await res2.json()
        console.log("custom_metadata")
        console.log("custom_metadata")
        console.log("custom_metadata")
        console.log("custom_metadata")
        console.log("custom_metadata")
        console.log("custom_metadata")
        console.log(custom_metadata)
        res.render("../views/channel", { // ---> /channel/lolgeranimo
            "title" : req.params.name,
            "path" : req.path,
            "scrapped_data_s3": scrapped_data_s3,
            "custom_metadata": custom_metadata
        })
    }

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
        } 

        let endpoint = transcript_s3_json;
        let response = await fetch(endpoint);
        console.log("endpoint transcript_s3_json=", endpoint);
        if (!response.ok) {
             throw new Error('HTTP error ' + response.status);
        }
        let transcript_json = await response.json()
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('transcript_res_json')
        console.log('xd')
        // console.log(transcript_json)
        vod.channel;
        vod.link_s3;
        vod.title;
        vod.id;
        res.render("../views/vod", { // ---> /channel/lolgeranimo
            "subtitle": vod.channel + ": " + vod.id,
            "transcript_json": transcript_json.segments,
            "vod": vod
        })
    }
}

