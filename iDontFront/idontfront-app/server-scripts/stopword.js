
async function stopwordz(oldString) {
    custom_stopwords = [ "so", "he's", "she's", "it's", "we're", "it"]
    const { removeStopwords, eng, fra } = require('stopword')
    let newString = removeStopwords(oldString)
    newString = removeStopwords(newString, custom_stopwords)
    
    return newString
    
}
// return loadModule()
module.exports = stopwordz;