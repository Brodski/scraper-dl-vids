
const prepWordTree  = require("./helpers/prepWordTree")
const getAnalysis  = require("./helpers/getAnalysis")
const getVodsCompleted  = require("./helpers/getVodsCompleted")


function getProfilePic(req, custom_metadata) {
    let profilePic;
    if (req.params.name == "lolgeranimo") {
        profilePic = "https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100"
    } 
    else {
        let firstKey = Object.keys(custom_metadata)[0]
        profilePic = custom_metadata[firstKey]?.logo
    }
    return profilePic
}


module.exports = { 
    getVodsCompleted, 
    prepWordTree,
    getAnalysis,
    getProfilePic
}






