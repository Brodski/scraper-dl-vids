const databaseSingleton = require("../controllers/helpers/DatabaseSingleton")

exports.homepage = async (req, res) => {
    db = new databaseSingleton();
    let [channelsStreamed, channelsZeroStreamed] = await db.getChannelsForHomepage()
    let channelsList = [...channelsStreamed, ...channelsZeroStreamed]
    // res.set('Cache-Control', `${res.getHeader("cache-control")}, s-maxage=3600`); // 1 hours
    res.render("../views/homepage", {
        "channelsList": channelsList
    }) 
}