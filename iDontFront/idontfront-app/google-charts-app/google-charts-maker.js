
async function googleChartsMaker() {
    const puppeteer = require('puppeteer');

    const RENDER_TIMEOUT_MS = 5000;

    const browser = await puppeteer.launch();

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

    const doChartStuff = await page.evaluate(() => {

        google.charts.load('current', {packages:['wordtree']});
        google.charts.setOnLoadCallback(drawChart); // callback

        function drawChart() {
            var data = google.visualization.arrayToDataTable(
                [ ['Phrases'], ['cats are better than dogs'], ['cats eat kibble'], ['cats are better than hamsters'], ['cats are awesome'], ['cats are people too'], ['cats eat mice'], ['cats meowing'], ['cats in the cradle'], ['cats eat mice'], ['cats in the cradle lyrics'], ['cats eat kibble'], ['cats for adoption'], ['cats are family'], ['cats eat mice'], ['cats are better than kittens'], ['cats are evil'], ['cats are weird'], ['cats eat mice'], ] 
            );  
            var options = {
            wordtree: {
                format: 'implicit',
                word: 'cats'
            }
            };
            var chart = new google.visualization.WordTree(document.querySelector("#wordtree_basic"));
            chart.draw(data, options);
        }
    });

    const getHtmlRenderedChart = await page.evaluate(() => {
        // if (!window.chart || typeof window.chart.getImageURI === 'undefined') {
        //     return null;
        //     }
        return document.querySelector("#wordtree_basic")
    })
    doChartStuff()
    let theChart = getHtmlRenderedChart()
    console.log("theChart")
    console.log(theChart)
    await browser.close();
    return theChart
}

module.exports = googleChartsMaker;