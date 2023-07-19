const configs = require("../configs")

// const get_vod_by_id = async (req, res) => {
exports.channel = async (req, res) => {
    // https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/each-channel/lolgeranimo.json
    // /channels/completed-jsons/each-channel/lolgeranimo.json
    const endpoint = configs.S3_BUCKET + configs.S3_EACH_CHANNEL_JSON + req.params.name + ".json"; 
    const response = await fetch(endpoint);

    console.log("");
    console.log("");
    console.log("");
    console.log("");
    console.log("");
    console.log("");
    console.log("");
    console.log("");
    console.log("");
    console.log("channel name=", req.params.name);
    console.log("channel name=", req.params.name);
    console.log("channel name=", req.params.name);
    console.log("endpoint", endpoint);
    if (!response.ok) {
        throw new Error('HTTP error ' + response.status);
    }
    let scrapped_data_s3 = await response.json()
    console.log("scrapped_data_s3")
    console.log(scrapped_data_s3)
    
    let channel;
    let id;
    let vod_title;
    let link_s3;
    let link_s3_vtt;
    let link_s3_json;
    
    // scrapped_data_s3 .sort((a,b) => parseInt(a.rownum) > parseInt(b.rownum) ? 1 : -1)
    for (let vod of scrapped_data_s3) {
        channel = vod.channel;
        id = vod.id;
        vod_title = vod.title;
        link_s3 = vod.link_s3; //mp3
        let lastPeriodIdx = link_s3.lastIndexOf('.');
        if (lastPeriodIdx !== -1) {
            const tempName = link_s3.substring(0, lastPeriodIdx);
            link_s3_vtt = tempName + ".vtt"                
            link_s3_json = tempName + ".json"            
            console.log("");        
            console.log(tempName);        
            console.log(link_s3_vtt);        
            console.log(link_s3_json);        
        } 
    }
    
    const endpoint2 = link_s3_json; 
    const response2 = await fetch(endpoint2);
    let transcribe_json = await response.json()

    res.transcribe_json = transcribe_json;
    res.render("../views/channel", {
        "title" : req.params.name,
        "scrapped_data_s3": scrapped_data_s3
    })
}


// scrapped_data_s3 = 
// [
//     {
//       channel: 'lolgeranimo',
//       id: '1861789415',
//       link_s3: 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/1861789415/2v2v2v2_Pushing_Gladiator-v1861789415.mp3',
//       title: '2v2v2v2_Pushing_Gladiator-v1861789415.mp3'
//     },
//     {
//       channel: 'lolgeranimo',
//       id: '1862390912',
//       link_s3: 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/1862390912/Can_we_get_GrandMaster_before_the_end_of_the_Season-v1862390912.mp3',
//       title: 'Can_we_get_GrandMaster_before_the_end_of_the_Season-v1862390912.mp3'
//     },
//     {
//       channel: 'lolgeranimo',
//       id: '1863373278',
//       link_s3: 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/1863373278/Can_we_get_GrandMaster_before_the_end_of_the_Season-v1863373278.mp3',
//       title: 'Can_we_get_GrandMaster_before_the_end_of_the_Season-v1863373278.mp3'
//     },
//     {
//       channel: 'lolgeranimo',
//       id: '1863728745',
//       link_s3: 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/vod-audio/lolgeranimo/1863728745/Some_Grinding_to_GrandMaster_with_no_mic_atm_just_gaming-v1863728745.mp3',
//       title: 'Some_Grinding_to_GrandMaster_with_no_mic_atm_just_gaming-v1863728745.mp3'
//     }
//   ]
