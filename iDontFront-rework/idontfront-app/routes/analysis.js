
const DatabaseSingleton = require("../controllers/helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");
const channelHelper = require("../controllers/channelHelper");

async function getAnalysisPage(req, res) {
    let analysisObj;
    let db = new DatabaseSingleton();
    let [resultsChan, fields2] = await db.getChannel(req.params.name)
    let [resultsVods, fields1] = await db.getVodById(req.params.id)
    let vods = resultsVods.map( x => new Vod(x))
    let channels = resultsChan.map( x => new Channel(x))
    if (vods.length == 0 || channels.length == 0) {
        console.error("BAD QUERY FOR CHANNELS! OR VODS (analysis)")
        return "failed_helper"
    }
    txtKey = process.env.BUCKET_DOMAIN + "/" + encodeURI(vods[0].getS3TxtKey());

    try {
        analysisObj = await channelHelper.getAnalysis(txtKey)
    }  catch (e) {
        return "failed_helper"
    }
    res.render("../views/analysisGPT", {
        "channel": channels[0],
        "vod": vods[0],
        "wordcloud": analysisObj.wordcloudSvg?.outerHTML,
        "freqWordPlot": analysisObj.freqWordPlot?.outerHTML,
        "badWordPlot": analysisObj.badWordPlot?.outerHTML,
        "word_counter": analysisObj.word_counter,
        "bad_words_counter": analysisObj.bad_words_counter,
        "word_counter_txt_all": analysisObj.word_counter_txt_all,
        "word_counter_100":  analysisObj.word_counter_100
    })
    return
}
module.exports = { getAnalysisPage }