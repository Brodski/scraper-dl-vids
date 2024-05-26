
// 80% from --> d3 gallery Word cloud:  https://observablehq.com/@d3/word-cloud
//
//
// everywordz_counter = [  [ 'just', 370 ],    [ 'im', 229 ],    [ 'right', 224 ],   [ 'dont', 206 ], ]
const fs = require('fs');
const { createCanvas } = require("canvas");
const { JSDOM } = require("jsdom");

async function loadModule(everywordz_counter) {
    let d3Cloud = require("d3-cloud")
    const d3 = await import('d3');
    console.log('Current Working Directory:', process.cwd());
    console.log('LD_LIBRARY_PATH:', process.env.LD_LIBRARY_PATH);
    
    const files = fs.readdirSync(process.cwd());
    console.log("files");
    console.log(files);
    // process.env.LD_LIBRARY_PATH = process.env.LAMBDA_TASK_ROOT + "/lib"
    if (process.env.IS_LAMBDA == "true") {
      const files2 = fs.readdirSync("/var/lang/lib");
      console.log("/var/lang/lib");
      console.log("files2");
      console.log(files2);

      
      // process.env.LD_LIBRARY_PATH =  process.env.LAMBDA_TASK_ROOT + "/lib" + (":" + process.env.LD_LIBRARY_PATH);
      process.env.LD_LIBRARY_PATH = process.env.LAMBDA_TASK_ROOT + "/lib"
      process.env.PKG_CONFIG_PATH = process.env.LAMBDA_TASK_ROOT + "/lib"
      process.env.PATH = process.env.PATH + ":" + process.env.LAMBDA_TASK_ROOT + "/lib"
      const files3 = fs.readdirSync( process.cwd() + "/lib");
      console.log('LD_LIBRARY_PATH 2:', process.env.LD_LIBRARY_PATH);
      console.log(process.cwd() + "/lib");
      console.log(files3);
    } 
    

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
        // const words = typeof text === "string" ? text.split(/\W+/g) : Array.from(text);
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
            
        // const colorScale = x => d3.interpolateCubehelixLong("purple", "orange")  (colorScaleAux(x)) 
        // const colorScale = x =>  d3.interpolateHslLong("red", "blue")   (colorScaleAux(x)) 
        // const colorScale = x =>  d3.interpolateHslLong("red", "#1b42ba")   (colorScaleAux(x)) 
        // const colorScale = x =>  d3.interpolateHslLong("#1b42ba", "orange")   (colorScaleAux(x)) 
        const colorScale = x =>  d3.interpolateHslLong("darkblue", "#980000")   (colorScaleAux(x)) 

        const data = d3.rollups(everywordz_counter, size, w => w)
          .slice(0, maxWords)
          .map(([key, size]) => ({text: word(key[0]), size: scaleFont(key[1]), freq: key[1] }));
        // console.log(date) ===> [
        //           { text: 'just', size: 180, freq: 370 },
        //           { text: 'im', size: 127.17579250720462, freq: 229 },
        //           { text: 'right', size: 125.30259365994236, freq: 224 }, ]
        
        const dom = new JSDOM(`<!DOCTYPE html><body></body>`);
        const window = dom.window;
        const document = window.document;
        
        // Create an SVG element using D3.js
        const svg = d3.select(document.body).append('svg')
          .attr("viewBox", [0, 0, width, height])
          .attr("width", width)
          .attr("font-family", fontFamily)
          .attr("text-anchor", "middle")
          .attr("style", "max-width: 100%; height: auto; height: intrinsic;");
        
        const g = svg.append("g").attr("transform", `translate(${marginLeft},${marginTop})`);
        const cloud = d3Cloud()
            .size([width - marginLeft - marginRight, height - marginTop - marginBottom])
            .canvas(() => createCanvas(1, 1))
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

      let wcSvg = WordCloud(everywordz_counter, {
        // width: 1250,
        // height: 800,
        width: 800,
        height: 500,
        size: (x) => { return x[0].length} 
        // size: (x) => { console.log(x); return x[0].length}  //+ Math.random(),
        // rotate: () => (~~(Math.random() * 6) - 3) * 30
    })
    return wcSvg
}
module.exports = loadModule;