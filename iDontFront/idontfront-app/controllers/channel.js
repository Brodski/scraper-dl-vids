const configs = require("../configs")
const plot  = require("../server-scripts/plot")
const wordcloud  = require("../server-scripts/wordcloud")
// https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json


// path = /channel/lolgeranimo
exports.channel = async (req, res) => {    
    // Get all channels
    const endpoint = configs.S3_BUCKET + configs.S3_EACH_CHANNEL_JSON + req.params.name + ".json";   //  https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/each-channel/lolgeranimo.json
    const response = await fetch(endpoint); // mocks/completed_captions_list.py
    if (!response.ok) {
         throw new Error('HTTP error ' + response.status);
    }
    let scrapped_data_s3 = await response.json()

    const endpoint2 = configs.S3_BUCKET + configs.S3_CUSTOM_METADATA_KEYBASE + req.params.name + "/custom-metadata.json";  //     /channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json    
    const res2 = await fetch(endpoint2); // mocks/completed_captions_list.py
    if (!res2.ok) {
         throw new Error('HTTP error ' + res2.status);
    }
    let custom_metadata = await res2.json();

    let transcript_s3_vtt;
    let transcript_s3_json;
    let transcript_s3_txt;
    let vod;
    // console.log("-----------------------------------------------------")
    // console.log("-----------------------------------------------------")
    // console.log("-----------------------------------------------------")
    // console.log("scrapped_data_s3")
    // console.log(scrapped_data_s3)
    // console.log("=====================================================")
    // console.log("=====================================================")
    // console.log("=====================================================")
    // console.log("custom_metadata")
    // console.log(custom_metadata)
    if (req.params.id != null) {
        vod = scrapped_data_s3.filter( vod => vod.id == req.params.id)[0]
        console.log("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        console.log("vod")
        console.log(vod)
        if (vod == null) {
            res.status(404)
            res.render('404', {
                msg: "😢 😞 😟 😭 😿"
            })
            return
        }
        let lastPeriodIdx = vod?.link_s3.lastIndexOf('.');
        if (lastPeriodIdx !== -1) {
            const tempName = vod.link_s3.substring(0, lastPeriodIdx);
            transcript_s3_vtt = tempName + ".vtt"                
            transcript_s3_json = tempName + ".json"
            transcript_s3_txt = tempName + ".txt"
        } 
    }
    //  ***************************************
    //  ***************************************
    //  ***************************************
    //  ***************************************
    //  CHANNEL PATH
    // 
    // 
    // http://localhost:3333/channel/lolgeranimo
    let profilePic;
    if (profilePic == null && req.params.name == "lolgeranimo") {
        profilePic = "https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100"
    }
    if (req.params.id == null) {

        const endpoint3 = configs.S3_BUCKET + configs.S3_STATE_OVERVIEW_JSON;   //  https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/each-channel/lolgeranimo.json
        const response3 = await fetch(endpoint3); // mocks/completed_captions_list.py
        let firstKey = Object.keys(custom_metadata)[0]
        profilePic = custom_metadata[firstKey]?.logo
        
        if (profilePic == null && req.params.name == "lolgeranimo") {
            profilePic = "https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100"
        }
        console.log(custom_metadata)
        console.log("custom_metadata")
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        console.log(" profilePic !!!!!!!!!!!! " + profilePic)
        let keys;
        let keysWithVtt = [];
        console.log("endpoint3=" + endpoint3)
        if (!response3.ok) {
            throw new Error('HTTP error ' + response3.status);
        }
        let overview_state = await response3.json()
        console.log("overview_state")
        // console.log(overview_state)
        if ( req.params.name in overview_state) {
    
            keys = Object.keys(overview_state[req.params.name]);
            console.log("keys")
            console.log(keys)
            keys.forEach(k => {
                let hasCaptions = false;
                for (let x of overview_state[req.params.name][k]) {
                    // console.log(x);
                    if (x.endsWith(".vtt")) {
                        hasCaptions = true;
                        keysWithVtt.push(k)
                    }
                }
            });
            console.log("keysWithVtt")
            console.log(keysWithVtt)
        }

        res.render("../views/channel", { // ---> /channel/lolgeranimo
            "title" : req.params.name,
            "path" : req.path,
            "scrapped_data_s3": scrapped_data_s3,
            "custom_metadata": custom_metadata,
            "keys": keysWithVtt,
            "profilePic": profilePic
        })
        return
    }
    



    //  ***************************************
    //  ***************************************
    //  ***************************************
    //  ***************************************
    //  VOD PATH
    // 
    // 
    if (req.params.id != null && !req.path.includes("/analysis") && !req.path.includes("/wordtree") ) {

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
            // "freqWord": freqWord.outerHTML
        })
        return
    }
    const txtAux = async () => {
        if (vod == null) {
            res.status(404).render('404')
        }
        let response = await fetch(transcript_s3_txt);
        if (!response.ok) {
             throw new Error('HTTP error ' + response.status);
        }
        return response
    }

    if (req.params.id != null && req.path.includes("/wordtree")) {
        let response = await txtAux();
        let res_transcript_txt = await response.text() // the .txt file
        let sentence_arr = res_transcript_txt.split(/\n+/)
        let sentence_arr2 = []
        for (let sent of sentence_arr) {
            let x = sent.replaceAll(/[.,?;:!]/g, '').split(' ')
            sentence_arr2.push([x.join(' ')])
        }
        // const googleChartsMaker = require("../server-scripts/google-charts-maker")
        // let googleChartsEle = await googleChartsMaker(sentence_arr2)
        res.render("../views/wordtree", {
            "sentence_arr": sentence_arr2,
            "channel": vod.channel,
            "vod": vod,
            "vod2": custom_metadata[req.params.id],
            "profilePic":profilePic
        })
        return
    }
    if (req.params.id != null && req.path.includes("/analysis")) {
        let response =  await txtAux();
        let res_transcript_txt = await response.text() // the .txt file
        let txt_arr = res_transcript_txt.split(/\s+/)

        const stopword  = require("../server-scripts/stopword")
        let txt_arr_stopwords = await stopword(txt_arr)
        console.log(txt_arr_stopwords)
        let stopwordz_counter_map = new Map();
        for (let word of txt_arr_stopwords) {
            // Do this here b/c stopword library
            word = word.replaceAll(/[.,!;:'?\+]/g, "");
            word = word.toLowerCase()
            if (stopwordz_counter_map.has(word)) {
                let count = stopwordz_counter_map.get(word)
                stopwordz_counter_map.set(word, count + 1)
            } else {
                stopwordz_counter_map.set(word, 1);
            }
        }
        const stopwordz_counter = [...stopwordz_counter_map.entries()].sort((a, b) => b[1] - a[1]);
        console.log(stopwordz_counter)



        let freqWord = await plot(stopwordz_counter)
        console.log("freqWord")
        console.log(freqWord)

        let wordcloudSvg = await wordcloud(stopwordz_counter)
        console.log("wordcloudSvg")
        console.log(wordcloudSvg)
        console.log("stopwordz_counter 1")
        console.log(stopwordz_counter)

        let bad_words = ["fuck", "shit", "bitch", "loser", "subhuman", "disgusting", "retard", "moron", "autistic", "cock", "dick", "cancer", "tumor"]
        let regex = new RegExp(`\\b(${bad_words.join('\\w*\\b|')})`, 'gi'); 
        let bad_words_counter = []
        for (let i=0; i < stopwordz_counter.length; i++) {
            if (regex.test(stopwordz_counter[i][0])) {
                // console.log(stopwordz_counter[i])
                bad_words_counter.push(stopwordz_counter[i])
            }
        }
        console.log(regex)
        console.log(regex)
        console.log(regex)
        console.log(regex)

        res.render("../views/analysis", { // ---> /channel/lolgeranimo
            "channel": vod.channel,
            // "transcript_json": transcript_json.segments,
            "vod": vod,
            "vod2": custom_metadata[req.params.id],
            // "transcript_s3_vtt": transcript_s3_vtt,
            // "transcript_s3_json": transcript_s3_json,
            // "transcript_s3_txt": transcript_s3_txt,
            "freqWord": freqWord.outerHTML,
            "stopwordz_counter": stopwordz_counter,
            "wordcloud": wordcloudSvg.outerHTML,
            "profilePic": profilePic,
            "bad_words_counter": bad_words_counter
        })
        return
    }
}

