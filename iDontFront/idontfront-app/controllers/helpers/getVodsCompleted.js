const configs = require("../../configs");

async function getVodsCompleted(channelName) {
    const endpoint3 = configs.S3_BUCKET + configs.S3_STATE_OVERVIEW_JSON;   // https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/each-channel/lolgeranimo.json
    const response3 = await fetch(endpoint3); // mocks/completed_captions_list.py

    let vodsCompleted = []; // completed if transcripts are present (ie VTT file is there)
    console.log("endpoint3=" + endpoint3)
    if (!response3.ok) {
        throw new Error('HTTP error ' + response3.status);
    }

    let overview_state = await response3.json()
    if ( channelName in overview_state) {
        vodIs = Object.keys(overview_state[channelName]);
        vodIs.forEach(k => {
            for (let x of overview_state[channelName][k]) {
                if (x.endsWith(".vtt")) {
                    vodsCompleted.push(k)
                }
            }
        });
        console.log("vodsCompleted")
        console.log(vodsCompleted)
    }
    return (vodsCompleted)    
}



module.exports = getVodsCompleted




