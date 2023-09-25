async function loadModule(stopwordz_counter) {
    // const myModule = await import('./index.js');
    
    const Plot = await import('@observablehq/plot');
    const d3 = await import('d3');
    // const { JSDOM } = require('jsdom');
    // const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');
    // document = dom.window.document;
    // const plot = Plot.rectY(stopwordz_counter, Plot.binX({y: "count"}, {x: "word",  fill: "steelblue"})).plot()

    let data = stopwordz_counter.slice(0, 140)
    console.log("data")
    console.log("data")
    console.log(data)
    // const colorScale =  d3.scaleSequential(d3.interpolateBlues).domain([-100 , Math.max(...data.map(d => d[1])) ]); // d3.interpolateBlues, which maps the range [0, 1], , from light to dark
    const colorScale = d3.scaleSequential().range(["lightblue", "darkblue"]).domain([0 , Math.max(...data.map(d => d[1])) ]);

    const plot = Plot.plot({
        // title: "Frequence of Words",
        marginTop: 10,
        marginRight: 20,
        marginleft: 50,
        marginBottom: 80,
        
        x: {
            label: "Count",
            fontSize: 26, 
            grid: true,
            paddingOuter: 30
        },
        y: {
            // tickRotate: -45,
            domain: data.map(d => d[0]),
        },
        width: 960,
        height: 2500,
        marks: [
            Plot.barX(data, { 
                y: d => d[0], 
                x: d => d[1], 
                fill: d => colorScale(d[1]),
                title: d => `${d[0]}: ${d[1]}`,
            }),
            Plot.text(data, {
                y: d => d[0], 
                x: d => d[1], 
                text: (d) => `${d[0]}: ${d[1]}`, 
                dy: -8, 
                dx: 12,
                lineAnchor: "bottom",
                fontFamily: "hacky-selector-text",
                fontSize: 14,
                fontWeight: 700,
            }),
            // Plot.text(["Frequence of Words"], {paddingTop: 30, lineWidth: 30, frameAnchor: "top", fontSize: 16, fontWeight: 700}),
        ],  
    });
    plot.id = "word-count-graph"
    return plot
}
module.exports = loadModule;