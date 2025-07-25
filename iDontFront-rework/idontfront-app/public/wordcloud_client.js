// https://d3-graph-gallery.com/graph/wordcloud_custom.html
// https://observablehq.com/@d3/word-cloud
function WordCloud(everywordz_counter, { 
    size = group => group.length + 0.1, // Given a grouping of words, returns the size factor for that word
    word = d => d,                // Given an item of the data array, returns the word
    // word = d => d[0],                // Given an item of the data array, returns the word
    // size = d => d[1], // Given a grouping of words, returns the size factor for that word
    marginTop = 0,                // top margin, in pixels
    marginRight = 0,              // right margin, in pixels
    marginBottom = 0,             // bottom margin, in pixels
    marginLeft = 0,               // left margin, in pixels
    width = 640,                  // outer width, in pixels
    height = 400,                 // outer height, in pixels
    maxWords = 110,               // maximum number of words to extract from the text
    fontFamily = "sans-serif",    // font family
    fontScale = 15,               // base font size
    padding = 0,                  // amount of padding between the words (in pixels)
    rotate = 0,                   // a constant or function to rotate the words
    invalidation                  // when this promise resolves, stop the simulation
    } = {}) {

    maxWords = (everywordz_counter.length > 110 ? 110 : everywordz_counter.length);
    const words = everywordz_counter.map( d => d[0])


    let minValue = everywordz_counter[maxWords - 1][1] // [just, 110]
    let maxValue = everywordz_counter[0][1]

    let scaleFont = d3.scaleLinear()
        .domain([minValue, maxValue])
        .range([28, 140]);
    
    // let colorScaleAux = d3.scaleLinear()
    let colorScaleAux = d3.scaleSqrt() // colorScaleAux(x) returns a value between [0-1]
        .domain([minValue, maxValue])
        .range([0, 1]);

    // original before dark-theme
    // const colorScale = x =>  d3.interpolateHslLong("darkblue", "#980000")   (colorScaleAux(x)) 
    // const colorScale = x => d3.interpolateHslLong("#00c6ff", "red")(colorScaleAux(x)); // GOOD
    const colorScale = x => d3.interpolateHslLong("#1eadd6", "#c92e2e")(colorScaleAux(x)); // GOOD // teal --->

    const data = d3.rollups(everywordz_counter, size, w => w)
        .slice(0, maxWords)
        .map(([key, size]) => ({text: word(key[0]), size: scaleFont(key[1]), freq: key[1] }));
    // console.log(data) ===> [
    //           { text: 'just', size: 180, freq: 370 },
    //           { text: 'im', size: 127.17579250720462, freq: 229 },
    //           { text: 'right', size: 125.30259365994236, freq: 224 }, ]
    
    // const dom = new JSDOM(`<!DOCTYPE html><body></body>`);
    // const window = dom.window;
    // const document = window.document;
    
    // Create an SVG element using D3.js
    // const svg = d3.select(document.body).append('svg')
    const svg = d3.select("#word-cloud-placeholder").append("svg")
        .attr("viewBox", [0, 0, width, height])
        .attr("width", width)
        .attr("font-family", fontFamily)
        .attr("text-anchor", "middle")
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;");
    
    const g = svg.append("g").attr("transform", `translate(${marginLeft},${marginTop})`);
    const cloud = d3.layout.cloud()
        .size([width - marginLeft - marginRight, height - marginTop - marginBottom])
        // .canvas(() => createCanvas(1, 1))
        .words(data)
        .padding(padding)
        .rotate(rotate)
        .font(fontFamily)
        // .fontSize(d => Math.sqrt(d[1]) * fontScale)
        .fontSize(d => scaleFont(d.freq))
        .on("word", ({size, x, y, rotate, text, freq}) => {
            g.append("text")
                .attr("font-size", size) // size = method created via fontSize()
                .attr("transform", `translate(${x},${y}) rotate(${rotate})`)
                .attr("fill", colorScale(freq))
                .text(text);
            });
    cloud.start();
    invalidation && invalidation.then(() => cloud.stop());
    return svg.node();
}


function gobabygo(everywordz_counter) {
    return WordCloud(everywordz_counter, {
        // width: 1250,
        // height: 800,
        width: 800,
        height: 500,
        size: (x) => { return x[0].length} 
    })
}