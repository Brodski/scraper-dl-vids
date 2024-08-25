const removeMoreStopWords = require("../../server-scripts/stopword")

async function prepWordTree(transcript_s3_txt) {
    console.log("fetching transcript_s3_txt", transcript_s3_txt)
    let response = await fetch(transcript_s3_txt);
    if (!response.ok) {
         throw new Error('HTTP error ' + response.status);
    }
    let res_transcript_txt = await response.text() // the .txt file

    let txt_arr = res_transcript_txt.split(/\s+/)

    const word_counter_txt_all = txt_arr.length
    console.log("word_counter_txt_all", word_counter_txt_all)
    const word_counter = removeMoreStopWords(txt_arr)
    // console.log("word_counter")
    // console.log(word_counter[0]) // ['just', 57] ==> word_counter[0][0] = most frequent word
    // console.log(word_counter.slice(0,20))
    
    // Get initial word for Wordtree on load.
    let wordtree_init = word_counter[0][0];
    for (let wrd of word_counter) {
        console.log(wrd)
        // if wrd[0] doenst have .,!;:'?
        if (wrd[1] < 51 && !['.', ',', '!', ';', ':', '\'', '?'].some(char => wrd[0].includes(char))) {
            wordtree_init = wrd[0]
            break
        }
    }

    let sentence_arrDirty = res_transcript_txt.split(/\. /)

    let sentence_arr = []
    for (let sent of sentence_arrDirty) {
        let x = sent.replaceAll(/[.,?;:!]/g, '').split(' ')
        sentence_arr.push([x.join(' ')])
    }
    return [sentence_arr, wordtree_init]
}

module.exports = prepWordTree