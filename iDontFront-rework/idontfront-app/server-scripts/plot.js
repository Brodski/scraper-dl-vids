
const { JSDOM } = require("jsdom");

async function plot_(everywordz_counter, chartTitle) {
    const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');    
    const Plot = await import('@observablehq/plot');
    const d3 = await import('d3');
    // const plot = Plot.rectY(everywordz_counter, Plot.binX({y: "count"}, {x: "word",  fill: "steelblue"})).plot()

    let data = everywordz_counter.slice(0, 40)
    if (data == null || data.length == 0) {
        return null
    }

    // y axis formating
    let last_data = data[data.length-1]
    let min_freq_data = last_data[1]
    let max_freq_data = data[0][1]
    let interval = Math.ceil(max_freq_data / 5);

    // light theme
    // const colorScale = d3.scaleSequential().range(["lightblue", "darkblue"]).domain([0 , Math.max(...data.map(d => d[1])) ]); 
    
    // dark theme
    const colorScale = d3.scaleSequential().range(["#15e199", "#1795eb"]).domain([0 , Math.max(...data.map(d => d[1])) ]); 

    const plot = Plot.plot({
        marginTop: 20,
        marginRight: 10,
        marginBottom: 80,
        marginLeft: 40,
        document: dom.window.document,
        // grid: true,
        // title: "Frequency of Words",
        // subtitle: "Subtitle to follow with additional context",
        // caption: "Figure 1. A chart with a title, subtitle, and caption.",
        
        y: {
            label: "Count",
            fontSize: 26, 
            grid: true,
            tickFormat: "d",
            domain: [0, max_freq_data + 1],
            ticks: 5, 
            // ticks: ((max_freq_data + 1) / 25), 
            // tickValues: Array.from({ length: 6 }, (_, i) => i * interval)
        },
        x: {
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
                // tip: true,
                fill: d => colorScale(d[1]),
                title: d => `${d[0]}: ${d[1]}`,
                // stroke: 'black',
            }),
            // Doesnt work b/c server-side
            // Plot.tip(data, Plot.pointerX( {x: d => d[0], y: d => d[1] })),

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

    plot.id = "word-count-graph"
    return plot
}
module.exports = plot_;