
async function googleChartsMaker(sentence_arr) {
    const puppeteer = require('puppeteer');

    const RENDER_TIMEOUT_MS = 5000;

    const browser = await puppeteer.launch({ headless: false });

    const page = await browser.newPage();
    page.setDefaultTimeout(RENDER_TIMEOUT_MS);
    page.on('pageerror', function(err) {
        throw new Error('Error: ' + err.toString());
    });
    let htmlContent = `
        <html>
            <head>
                <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                <script type="text/javascript">
                </script>
            </head>
            <body>
                <div id="wordtree_basic" style="width: 900px; height: 500px;"></div>
            </body>
        </html>
    `
    await page.setContent(htmlContent);

    console.log("sentence_arr")
    console.log("sentence_arr")
    console.log("sentence_arr")
    console.log("sentence_arr")
    console.log("sentence_arr")
    console.log("sentence_arr")
    console.log("sentence_arr")
    console.log(sentence_arr)
    const doChartStuff = await page.evaluate((sentence_arr) => {
        let div = document.createElement("div")
        div.innerText = 'yessssssssssssssssssss ' + sentence_arr
        document.body.appendChild(div)
        
        google.charts.load('current', {packages:['wordtree']});
        google.charts.setOnLoadCallback(drawChart); // callback
        function drawChart() {
            console.log("sentence_arrxxxxxxxxxxxxxxxxxxxxxx")
            console.log(sentence_arr)
            console.log(sentence_arr)
            var data = google.visualization.arrayToDataTable(
                sentence_arr
                // [ ['Phrases'], ['cats are better than dogs'], ['cats eat kibble'], ['cats are better than hamsters'], ['cats are awesome'], ['cats are people too'], ['cats eat mice'], ['cats meowing'], ['cats in the cradle'], ['cats eat mice'], ['cats in the cradle lyrics'], ['cats eat kibble'], ['cats for adoption'], ['cats are family'], ['cats eat mice'], ['cats are better than kittens'], ['cats are evil'], ['cats are weird'], ['cats eat mice'], ] 
            );  
            var options = {
            wordtree: {
                format: 'implicit',
                type: 'suffix',
                // word: 'cats'
            }
            };
            var chart = new google.visualization.WordTree(document.querySelector("#wordtree_basic"));
            chart.draw(data, options);
        }
    }, sentence_arr);

    // await page.setContent('<div id="myElement">Hello, World!</div>');
    await page.waitForFunction(() => document.querySelector('#wordtree_basic svg') != null );
    console.log("DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    console.log("DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    console.log("DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    // await page.waitForTimeout(5000)
    const theHtmlRenderedChart = await page.evaluate(() => {
        // if (!window.chart || typeof window.chart.getImageURI === 'undefined') { return null; }
        return document.querySelector("#wordtree_basic").outerHTML
    })
    // console.log("theHtmlRenderedChart")
    // console.log(theHtmlRenderedChart)
    await browser.close();
    return theHtmlRenderedChart
}

module.exports = googleChartsMaker;