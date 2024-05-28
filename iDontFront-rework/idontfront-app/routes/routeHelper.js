const channelHelper = require("../controllers/channelHelper");
const DatabaseSingleton = require("../controllers/helpers/DatabaseSingleton");
const Vod = require("../models/Vod");
const Channel = require("../models/Channel");
const { getChannelPage } = require("./channel");
const { getVodPage } = require("./vod");
const { getWordtreePage } = require("./wordtree");
const { getAnalysisPage } = require("./analysis");
// https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/channels/completed-jsons/custom-metadata/lolgeranimo/custom-metadata.json


// path = /channel/lolgeranimo
exports.routeHelper = async (req, res) => { 
    console.log("-----------------------------------------------------")
    console.log(req.path)
    console.log(req.path.endsWith("/btest"))
    console.log((req.params))
    console.log((req.params.id == null))
    //  ***************************************
    //  CHANNEL
    //  ***************************************
    if ((req.params.id == null) && req.path.endsWith("/btest")) {
        getChannelPage(req, res)
    }
    else if (req.params.id == null) {
        getChannelPage(req, res)
    }

    //  ***************************************
    //  CHANNEL - VOD 
    //  ***************************************
    if (req.params.id != null && !req.path.includes("/analysis") && !req.path.includes("/wordtree") ) {
        getVodPage(req, res);
    }

    //  ***************************************
    //  CHANNEL - VOD - WORDTREE
    //  ***************************************
    if (req.params.id != null && req.path.includes("/wordtree")) {
        getWordtreePage(req, res);
    }
    //  ***************************************
    //  CHANNEL - VOD - ANALYSIS
    //  ***************************************
    if (req.params.id != null && req.path.includes("/analysis")) {
        getAnalysisPage(req, res);

    }

}

