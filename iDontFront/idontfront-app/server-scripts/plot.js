
const { JSDOM } = require("jsdom");

async function loadModule(stopwordz_counter, chartTitle) {
    const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');
    // let document = dom.window.document;
    // const myModule = await import('./index.js');
    
    const Plot = await import('@observablehq/plot');
    const d3 = await import('d3');
    // const { JSDOM } = require('jsdom');
    // const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');
    // document = dom.window.document;
    // const plot = Plot.rectY(stopwordz_counter, Plot.binX({y: "count"}, {x: "word",  fill: "steelblue"})).plot()

    let data = stopwordz_counter.slice(0, 40)
    console.log("data")
    console.log("data")
    console.log(data)
    // const colorScale =  d3.scaleSequential(d3.interpolateBlues).domain([-100 , Math.max(...data.map(d => d[1])) ]); // d3.interpolateBlues, which maps the range [0, 1], , from light to dark
    const colorScale = d3.scaleSequential().range(["lightblue", "darkblue"]).domain([0 , Math.max(...data.map(d => d[1])) ]);

    const plot = Plot.plot({
        marginTop: 20,
        marginRight: 10,
        marginBottom: 80,
        marginLeft: 40,
        document: dom.window.document,
        // grid: true,
        // title: "Frequency of Words",
        // title: "For charts, an informative title",
        // subtitle: "Subtitle to follow with additional context",
        // caption: "Figure 1. A chart with a title, subtitle, and caption.",
        
        y: {
            label: "Count",
            fontSize: 26, 
            grid: true,
        },
        x: {
            // label: "Words",
            tickRotate: -45,
            domain: data.map(d => d[0]),
        },
        width: 960,
        height: 500,
        marks: [
            Plot.barY(data, { 
                x: d => d[0], 
                y: d => d[1], 
                // tip: "x", // tip doesnt work b/c server-side
                // tip: true
                fill: d => colorScale(d[1]),
                title: d => `${d[0]}: ${d[1]}`,
                // stroke: 'black',
            }),
            // Doesnt work b/c server-side
            //
            // Plot.tip(data, Plot.pointerX( {x: d => d[0], y: d => d[1] })),
            // Plot.tip(['partyin the usa'], {x: "just", y: 111 } ),

            // text above every bar
            Plot.text(data, {
                x: d => d[0], 
                y: d => d[1], 
                text: (d) => `${d[0]}: ${d[1]}`, 
                dy: -8, 
                dx: 12,
                lineAnchor: "bottom",
                fontFamily: "hacky-selector-text",
                fontSize: 14,
                fontWeight: 700,

                // filter: (_, i) => i % 5 === 4,
            }),
            // 'title'
            Plot.text([chartTitle], {lineWidth: 30, frameAnchor: "top", fontSize: 16, fontWeight: 700}),
            
            // Plot.ruleY([-10, 0, 10])
        ],  
    });
    console.log("plot!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    console.log("plot!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    console.log(plot)
    plot.id = "word-count-graph"
    return plot
}
module.exports = loadModule;