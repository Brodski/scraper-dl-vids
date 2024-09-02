
const prepWordTree  = require("./helpers/prepWordTree")
const getAnalysis  = require("./helpers/getAnalysis")


function getProfilePic(req, custom_metadata) {
    let firstKey = Object.keys(custom_metadata)[0]
    let profilePic = custom_metadata[firstKey]?.logo
    return profilePic
}


module.exports = { 
    prepWordTree,
    getAnalysis,
    getProfilePic
}






