
// 80% from --> d3 gallery Word cloud:  https://observablehq.com/@d3/word-cloud
//
//
// stopwordz_counter = [  [ 'just', 370 ],    [ 'im', 229 ],    [ 'right', 224 ],   [ 'dont', 206 ], ]
async function loadModule(stopwordz_counter) {
    let d3Cloud = require("d3-cloud")
    const d3 = await import('d3');

    // function WordCloud(text, {
    function WordCloud(stopwordz_counter, { 
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
        // const words = typeof text === "string" ? text.split(/\W+/g) : Array.from(text);
        const words = stopwordz_counter.map( d => d[0])

        let minValue = stopwordz_counter[maxWords - 1][1] // [just, 110]
        let maxValue = stopwordz_counter[0][1]

        let scaleFont = d3.scaleLinear()
            .domain([minValue, maxValue])
            .range([28, 140]);
        
        // let colorScaleAux = d3.scaleLinear()
        let colorScaleAux = d3.scaleSqrt() // colorScaleAux(x) returns a value between [0-1]
            .domain([minValue, maxValue])
            .range([0, 1]);
            
        // const colorScale = x => d3.interpolateCubehelixLong("purple", "orange")  (colorScaleAux(x)) 
        // const colorScale = x =>  d3.interpolateHslLong("red", "blue")   (colorScaleAux(x)) 
        const colorScale = x =>  d3.interpolateHslLong("red", "#1b42ba")   (colorScaleAux(x)) 


        console.log("colorScale 370")
        console.log(colorScale(370))
        console.log(colorScale(370))
        console.log(colorScale(0))

        console.log(stopwordz_counter)
        console.log("words v")
        console.log(words)

        const data = d3.rollups(stopwordz_counter, size, w => w)
          .slice(0, maxWords)
          .map(([key, size]) => ({text: word(key[0]), size: scaleFont(key[1]), freq: key[1] }));
        // console.log(date) ===> [
        //           { text: 'just', size: 180, freq: 370 },
        //           { text: 'im', size: 127.17579250720462, freq: 229 },
        //           { text: 'right', size: 125.30259365994236, freq: 224 }, ]
        
          const svg = d3.create("svg")
            .attr("viewBox", [0, 0, width, height])
            .attr("width", width)
            .attr("font-family", fontFamily)
            .attr("text-anchor", "middle")
            .attr("style", "max-width: 100%; height: auto; height: intrinsic;");
        
        const g = svg.append("g").attr("transform", `translate(${marginLeft},${marginTop})`);
        const cloud = d3Cloud()
            .size([width - marginLeft - marginRight, height - marginTop - marginBottom])
            .words(data)
            .padding(padding)
            .rotate(rotate)
            .font(fontFamily)
            // .fontSize(d => Math.sqrt(d[1]) * fontScale)
            .fontSize(d => scaleFont(d.freq))
            .on("word", ({size, x, y, rotate, text, freq}) => {
                g.append("text")
                    .attr("font-size", size) // size = method created via fontSize()
                    // .attr("font-size", scaleFont(freq))
                    .attr("transform", `translate(${x},${y}) rotate(${rotate})`)
                    .attr("fill", colorScale(freq))
                    .text(text);
                });
      
        cloud.start();
        invalidation && invalidation.then(() => cloud.stop());
        return svg.node();
      }

      let wcSvg = WordCloud(stopwordz_counter, {
        width: 1250,
        height: 800,
        size: (x) => { return x[0].length} 
        // size: (x) => { console.log(x); return x[0].length}  //+ Math.random(),
        // rotate: () => (~~(Math.random() * 6) - 3) * 30
    })
    return wcSvg
}
module.exports = loadModule;