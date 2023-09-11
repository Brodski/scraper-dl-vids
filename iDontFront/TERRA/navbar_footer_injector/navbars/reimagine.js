const https = require('https');

let getHtml = async function() {
    console.log('Hello from module.js');
    getJson()
}


// zip -r my_lambda.zip navbar_footer_injector/
// zip -r my_lambda.zip navbar_footer_injector/
// zip -r my_lambda.zip navbar_footer_injector/
// zip -r my_lambda.zip navbar_footer_injector/
// zip -r my_lambda.zip navbar_footer_injector/
// zip -r my_lambda.zip navbar_footer_injector/
async function getJson(subdomain="www", language="en", env="prod") {
    return new Promise(async (resolve, reject) => {
        const DEV_JSON = "https://dev-funky-fresh-webdev-work-bucket-baby123.s3.amazonaws.com"
        // const PROD_JSON = "https://prod-cdn-work-test.bski.one/reimagineTopnavConfigs.json"

        // environments
        const DEV_BUCKET = "https://dev-funky-fresh-webdev-work-bucket-baby123.s3.amazonaws.com"
        const PROD_BUCKET = "https://prod-cdn-work-test.bski.one"

        // json configs
        const EN_PATH = "/www/en/reimagineTopnavConfigs.json"
        const DE_PATH = "/www/de/reimagineTopnavConfigs.json"
        const FR_PATH = "/www/fr/reimagineTopnavConfigs.json"
        const ES_PATH = "/www/es/reimagineTopnavConfigs.json"
        const PT_PATH = "/www/fr/reimagineTopnavConfigs.json"
        const JA_PATH = "/www/ja/reimagineTopnavConfigs.json"
        const DEVELOPER_PATH = "/developer/devPortalTopNavConfig.json"
        const DOCS_PATH = "/docs/docsTopNavConfig-ft.json"
        const SUPPORT_PATH = "/support/supportHeader.json"


        switch(env) {
            case "prod":
                domainEnv = PROD_BUCKET
                break;
            case "stage":
                domainEnv = PROD_BUCKET
                break;
            case "dev":
                domainEnv = DEV_BUCKET
                break;
            default:
                domainEnv = PROD_BUCKET
        }


        let pathConfig = ""
        let domainEnv = ""
        switch(subdomain) {
            case "developer":
                pathConfig = DEVELOPER_PATH
                break;
            case "docs":
                pathConfig = DOCS_PATH
                break;
            case "support":
                pathConfig = SUPPORT_PATH
                break;
            default:
                pathConfig = EN_PATH
        }
        if (subdomain == "www") {
            switch(language) {
                case "en":
                    pathConfig = EN_PATH
                    break;
                case "de":
                    pathConfig = DE_PATH
                    break;
                case "fr":
                    pathConfig = FR_PATH
                    break;
                case "es":
                    pathConfig = ES_PATH
                    break;
                case "pt":
                    pathConfig = PT_PATH
                    break;
                case "ja":
                    pathConfig = JA_PATH
                    break;
                default: 
                    pathConfig = EN_PATH
                } 

        }
        url = domainEnv + pathConfig
        console.log(DEV_JSON + EN_PATH)
        console.log(DEV_JSON + EN_PATH)
        console.log(DEV_JSON + EN_PATH)
        const req = https.get((DEV_JSON + EN_PATH), (res) => {
            let data = '';
            let obj = {};

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                console.log('')
                console.log('we are back baby')
                console.log('')
                obj = JSON.parse(data);
                resolve(data);
            });
        })
        req.on("error", (err) => {
            console.log("Error: " + err.message);
            reject(e);
        });
    })
}

module.exports = getHtml;