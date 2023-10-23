


function stopwordz(oldString) {
    const { removeStopwords, eng, fra } = require('stopword')
    custom_stopwords = [ "so", "he's", "she's", "it's", "we're", "it"]
    let newString = removeStopwords(oldString)
    newString = removeStopwords(newString, custom_stopwords)
    
    return newString
    
}
module.exports = stopwordz;