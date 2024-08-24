
const { removeStopwords, eng, fra } = require('stopword')


function removeMoreStopWords(txt_arr) { 
    let txt_arr_no_stopwords = stopwordz(txt_arr)

    let word_counter = new Map();
    for (let word of txt_arr_no_stopwords) {
        // Do this here b/c stopword library
        // word = word.replaceAll(/[.,!;:'?\+]/g, ""); // REMOVED THE COMMA ????
        word = word.replaceAll(/[.,!;:?\+]/g, "");
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

function stopwordz(oldString) {
    custom_stopwords = [ "so", "he's", "she's", "it's", "we're", "it"]
    let newString = removeStopwords(oldString)
    newString = removeStopwords(newString, custom_stopwords)
    
    return newString    
}

module.exports = removeMoreStopWords;