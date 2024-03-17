const configs = require("../configs")
const databaseSingleton = require("./helpers/DatabaseSingleton")

// const get_vod_by_id = async (req, res) => {
exports.homepage = async (req, res) => {

    db = new databaseSingleton();
    db.printHi()
    channelsList = await db.getChannelsForHomepage(); // type = models/Channel.js
    // console.log("homepage's channelsList:", channelsList)
    
    res.render("../views/homepage", {
        "channelsList": channelsList
    }) 
}