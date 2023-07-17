const configs = require("../configs")

// const get_vod_by_id = async (req, res) => {
exports.get_vod_by_id = async (req, res) => {
    const endpoint = configs.S3_BUCKET + configs.S3_STATE_OVERVIEW_JSON
    console.log("ENDPOINT = ", endpoint)
    console.log("configs.S3_BUCKET = ", configs.S3_BUCKET)
    // const id = req.params.id
    
    // res.render("./transcripts/searchResults", {
    //     h2: "Vod id: " + id,
    //     search: id, 
    //     results: [vod]
    // })
    // res.render("<div> bam </div>")
    const response = await fetch(endpoint);
    if (!response.ok) {
        throw new Error('HTTP error ' + response.status);
    }
    let data = await response.json()
    Object.keys(data).forEach( (chann) => {
        console.log(chann)
        console.log(data[chann])
    })
    // for (const x of data) {
    //     // console.log(x)
    //     console.log()
    //     console.log(x)
    //     // console.log(x.channel)
    //     // console.log(x.link_s3)
    //     // let link = x.link_s3
    //     // let extIndex = link.lastIndexOf('.');
    //     // let substringz = link.substring(0,extIndex)
    //     // console.log(substringz)
    // }
    // console.log(data)
    // console.log(data)
    // .then(response => response.json())
    // .then(data => console.log(data))
    // .catch((error) => console.error('Error:', error));
    res.render('index', { title: 'Home' });
}

// module.exports = []