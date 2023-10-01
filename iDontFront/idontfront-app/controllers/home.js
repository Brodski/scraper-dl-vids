const configs = require("../configs")

// const get_vod_by_id = async (req, res) => {
exports.homepage = async (req, res) => {
    const endpoint = configs.S3_BUCKET + configs.S3_STATE_OVERVIEW_LIGHT_JSON
    const response = await fetch(endpoint);
    if (!response.ok) {
        throw new Error('HTTP error ' + response.status);
    }
    let overviewLight = await response.json()
    for (let chann of overviewLight) {
        console.log("channXz")
        console.log(chann)
    }
    
    res.render("../views/homepage", {
        "overviewLight": overviewLight
    }) 
}

// overviewLight = [
//   {
//     channel: 'lolgeranimo',
//     size: 4,
//     path: 'channels/completed-jsons/each-channel/lolgeranimo.json',
//     rownum: '-1',
//     twitchurl: 'https://www.twitch.tv/lolgeranimo',
//     displayname: 'LoLGeranimo',
//     logo: 'https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100'
//   },
//   {
//     channel: 'lck',
//     size: 1,
//     path: 'channels/completed-jsons/each-channel/lck.json',
//     rownum: '9999',
//     twitchurl: null,
//     displayname: null,
//     logo: null
//   }
// ]