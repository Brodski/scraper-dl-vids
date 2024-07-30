async function prepWordTree(transcript_s3_txt) {
    console.log("fetching transcript_s3_txt", transcript_s3_txt)
    let response = await fetch(transcript_s3_txt);
    if (!response.ok) {
         throw new Error('HTTP error ' + response.status);
    }
    let res_transcript_txt = await response.text() // the .txt file

    // let sentence_arrDirty = res_transcript_txt.split(/\n+/)
    let sentence_arrDirty = res_transcript_txt.split(/\. /)

    let sentence_arr = []
    for (let sent of sentence_arrDirty) {
        let x = sent.replaceAll(/[.,?;:!]/g, '').split(' ')
        sentence_arr.push([x.join(' ')])
    }
    return sentence_arr
}

module.exports = prepWordTree