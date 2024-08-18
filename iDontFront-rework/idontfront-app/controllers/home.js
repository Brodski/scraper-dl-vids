const databaseSingleton = require("./helpers/DatabaseSingleton")

exports.homepage = async (req, res) => {
    db = new databaseSingleton();
    channelsList = await db.getChannelsForHomepage(); // type = models/Channel.js
    
    res.render("../views/homepage", {
        "channelsList": channelsList
    }) 
}