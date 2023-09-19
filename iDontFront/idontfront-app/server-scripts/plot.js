
// node_modules\@observablehq\plot\src\context.js
// import { JSDOM } from "jsdom";
// const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');
//
// document = dom.window.document;


async function loadModule(stopwordz_counter) {
    // const myModule = await import('./index.js');
    
    const Plot = await import('@observablehq/plot');
    const d3 = await import('d3');
    const { JSDOM } = require('jsdom');
    const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');
    document = dom.window.document;
    console.log("plot js")
    console.log("plot js")
    console.log("plot js")
    console.log("plot js")
    // console.log(Plot)
    // const plot = Plot.rectY({length: 10000}, Plot.binX({y: "count"}, {x: Math.random})).plot();
    // const plot = Plot.rectY(unemployment, Plot.binX({y: "count"}, {x: "rate"})).plot()
    // const plot = Plot.rectY(stopwordz_counter, Plot.binX({y: "count"}, {x: "word",  fill: "steelblue"})).plot()
    let cnt = 0
    complex_obj = []
    // [ [ 'just', 370 ],    [ 'im', 229 ],    [ 'right', 224 ],   [ 'dont', 206 ], ... ]
    console.log("stopwordz_counter")
    console.log(stopwordz_counter)
    for ( let word_kv of stopwordz_counter) {
        cnt = cnt + 1
        if (cnt > 30) {
            break
        }
        let myObj = {}
        myObj[word_kv[0]] = word_kv[1]
        complex_obj.push( myObj )
    }
    console.log('complex_obj')
    console.log('complex_obj')
    console.log(complex_obj)
    let data = stopwordz_counter.slice(0, 40)
    const plot = Plot.plot({
        title: "Frequence of Words",
        marginTop: 20,
        marginRight: 20,
        marginBottom: 80,
        marginLeft: 40,
        grid: true,
        title: "For charts, an informative title",
        subtitle: "Subtitle to follow with additional context",
        // caption: "Figure 1. A chart with a title, subtitle, and caption.",
        
        y: {
            label: "Count",
        },
        x: {
            label: "Words",
            tickRotate: -45,
            domain: data.map(d => d[0])
        },
        marks: [
            Plot.barY(data, { 
                x: d => d[0], 
                y: d => d[1], 
                // tip: "x",
                // tip: true
                title: d => `test ${d[1]}`,
            }),
            // Doesnt work b/c server-side
            //
            // Plot.tip(data, Plot.pointerX( {x: d => d[0], y: d => d[1] })),
            // Plot.tip(['partyin the usa'], {x: "just", y: 111 } ),

            // text above every bar
            Plot.text(data, {
                x: d => d[0], 
                y: d => d[1], 
                text: (d) => d[1], 
                dy: -6, 
                lineAnchor: "bottom",
                // filter: (_, i) => i % 5 === 4,
            }),
            // 'title'
            Plot.text(["Frequence of Words"], {lineWidth: 30, frameAnchor: "top", fontSize: 16, fontWeight: 700}),
            
            // Plot.ruleY([-10, 0, 10])
        ],  
    });
    console.log("plot!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    console.log("plot!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    console.log(plot)
    plot.id = "SUPERID"
    // return "buttlol"
    return plot
}
// return loadModule()
module.exports = loadModule;