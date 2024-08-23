const { getChannelPage } = require("./channel");
const { getVodPage } = require("./vod");
const { getWordtreePage } = require("./wordtree");
const { getAnalysisPage } = require("./analysis");
// https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json


exports.routeHelper = async (req, res) => { 
    let msg;
    //  ***************************************
    //  CHANNEL
    //  ***************************************
    if (req.params.id == null) {
        msg = await getChannelPage(req, res)
    }
    //  ***************************************
    //  CHANNEL - VOD 
    //  ***************************************
    if (req.params.id != null && !req.path.includes("/analysis") && !req.path.includes("/wordtree") ) {
        msg = await getVodPage(req, res);
    }
    //  ***************************************
    //  CHANNEL - VOD - WORDTREE
    //  ***************************************
    if (req.params.id != null && req.path.includes("/wordtree")) {
        msg = await getWordtreePage(req, res);
    }
    //  ***************************************
    //  CHANNEL - VOD - ANALYSIS
    //  ***************************************
    if (req.params.id != null && req.path.includes("/analysis")) {
        msg = await getAnalysisPage(req, res);
    }
    if (msg == "failed_helper") {
        res.status(404)
        res.render("../views/404", {})
    }
}

