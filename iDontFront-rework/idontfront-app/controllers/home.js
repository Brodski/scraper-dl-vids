const databaseSingleton = require("./helpers/DatabaseSingleton")

exports.homepage = async (req, res) => {
    db = new databaseSingleton();
    // channelsList = await db.getChannelsForHomepage();
    
    let [channelsStreamed, channelsZeroStreamed] = await db.getChannelsForHomepage()
    let channelsList = [...channelsStreamed, ...channelsZeroStreamed]
    console.log("channelsList")
    console.log("channelsList")
    console.log("channelsList")
    console.log("channelsList")
    console.log("channelsList")
    console.log("channelsList")
    console.log("channelsList")
    console.log("channelsList")
    console.log("channelsList")
    console.log(channelsList)
    res.render("../views/homepage", {
        "channelsList": channelsList
    }) 
}