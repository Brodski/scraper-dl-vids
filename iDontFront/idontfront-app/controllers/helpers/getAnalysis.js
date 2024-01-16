
const stopword = require("../../server-scripts/stopword")
const plot  = require("../../server-scripts/plot")
const wordcloud  = require("../../server-scripts/wordcloud")

async function getAnalysis(transcript_s3_txt) {
    console.log("getAnalysis transcript_s3_txt")
    console.log("getAnalysis transcript_s3_txt")
    console.log(transcript_s3_txt)

    let bad_words = ["fuck", "shit", "bitch", "loser", "subhuman", "disgusting", "retard", "moron", "autistic", "cock", "dick", "cancer", "tumor"]
    
    let regex = new RegExp(`\\b(${bad_words.join('\\w*\\b|')})`, 'gi'); 

    let response = await fetch(transcript_s3_txt);
    if (!response.ok) {
         throw new Error('HTTP error ' + response.status);
    }

    let res_transcript_txt = await response.text() // the .txt file
    let txt_arr = res_transcript_txt.split(/\s+/)
    const word_counter = removeStopWords(txt_arr)
    const bad_words_counter = word_counter.filter(([word]) => regex.test(word));

    // const word_counter = [...word_counter.entries()].sort((a, b) => b[1] - a[1]);
    console.log("word_counter")
    console.log(word_counter)
    
    let freqWordPlot = await plot(word_counter, "Frequency of Words")
    console.log("freqWordPlot")
    console.log(freqWordPlot)

    let badWordPlot = await plot(bad_words_counter, "Frequency of Swear Words")
    console.log("badWordPlot")
    console.log(badWordPlot)
    
    let wordcloudSvg = await wordcloud(word_counter)
    console.log("wordcloudSvg")
    console.log(wordcloudSvg)


    console.log(regex)
    console.log(regex)
    console.log(regex)
    console.log(regex)
    console.log("bad_words_counter")
    console.log(bad_words_counter)
    return {freqWordPlot, badWordPlot, wordcloudSvg, bad_words_counter, word_counter}
}


function removeStopWords(txt_arr) {
    let txt_arr_no_stopwords = stopword(txt_arr)

    let word_counter = new Map();
    for (let word of txt_arr_no_stopwords) {
        // Do this here b/c stopword library
        word = word.replaceAll(/[.,!;:'?\+]/g, "");
        word = word.toLowerCase()
        if (word_counter.has(word)) {
            let count = word_counter.get(word)
            word_counter.set(word, count + 1)
        } else {
            word_counter.set(word, 1);
        }
    }
    word_counter = [...word_counter.entries()].sort((a, b) => b[1] - a[1]);
    return word_counter
}


module.exports = getAnalysis