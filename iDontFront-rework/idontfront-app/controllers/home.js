const databaseSingleton = require("./helpers/DatabaseSingleton")

exports.homepage = async (req, res) => {
    db = new databaseSingleton();
    channelsList = await db.getChannelsForHomepage();
    
    res.render("../views/homepage", {
        "channelsList": channelsList
    }) 
}