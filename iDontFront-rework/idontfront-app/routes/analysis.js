
const DatabaseSingleton = require("../controllers/helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");
const channelHelper = require("../controllers/channelHelper");

async function getAnalysisPage(req, res) {
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
        "wordcloud": analysisObj.wordcloudSvg?.outerHTML,
        "freqWordPlot": analysisObj.freqWordPlot?.outerHTML,
        "badWordPlot": analysisObj.badWordPlot?.outerHTML,
        "word_counter": analysisObj.word_counter,
        "bad_words_counter": analysisObj.bad_words_counter,
    })
    return
}
module.exports = { getAnalysisPage }