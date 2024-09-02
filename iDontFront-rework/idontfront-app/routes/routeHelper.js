const { getChannelPage } = require("./channel");
const { getVodPage } = require("./vod");
const { getWordtreePage } = require("./wordtree");
const { getAnalysisPage } = require("./analysis");

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
    // if (req.params.id != null && req.path.includes("/wordtree")) {
    //     msg = await getWordtreePage(req, res);
    // }
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

