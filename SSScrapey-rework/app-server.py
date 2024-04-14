from __future__ import unicode_literals
from flask import Flask
from routes.testz import test_bp
from routes.everythingRoutes import everything_bp, ranking_bp
# from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort

# import youtube_dl

app = Flask(__name__)
app.register_blueprint(test_bp, url_prefix='/test')
app.register_blueprint(ranking_bp, url_prefix='/ranking')
app.register_blueprint(everything_bp)

@app.route('/yo/<text>')
@app.route('/yo/')
def yo(text="brother"):
    return "Yo {} @ {}".format(text, app.root_path)


@app.errorhandler(404)
def page_not_found(error):
    err = "Resource not found :(" if error is None else error
    # This works too
    # response = jsonify({"error": error.description}) 
    response = jsonify({"error": str(err)})
    response.status_code = 404
    return response


@app.errorhandler(400)
def conflict_error(error):
    response = jsonify({"error":  error.description})
    response.status_code = 400
    return response


@app.route('/')
def home():
    # Links to all other routes in the app.
    return """
    <h1>Links to all other routes in the app.</h1>
    <hr/>
    <h3> Micro Preper </h3>
        <li><a href="/main/ranking/kickit">  mainController.kickit(True) </a></li>
        <li><a href="/main/ranking/kickit_real">  mainController.kickit(<b>False</b>) </a></li>
            <ul>
                <li><a href="/ranking/getTopChannels"> Sullygnome -----> createToDoController.getTopChannels() </a></li>
                <li><a href="/hrefGet/scrape4VidHref/mock"> Selenium -----> seleniumController.scrape4VidHref() </a></li>
            </ul>
        </li>
    <hr/>
    <h3> Micro Downloader </h3>     
        <li><a href="/main/kickDownloader">  mainController.kickDownloader(Debug=TRUE)  </a></li>
        <li><a href="/main/kickDownloader_real">  mainController.kickDownloader(<b>Debug=FALSE</b>) </a></li>
            <ul>
            </ul>
        </li>
    <hr/>
    
    <h3> Micro Transcriber </h3>
        <li><a href="/main/kickTranscriber/kickIt">   mainController.kickWhisperer(Debug=True) </a></li>
        <li><a href="/main/kickTranscriber/kickIt_real">   mainController.kickWhisperer(<b>Debug=FALSE</b>) </a></li>
        <ul>
            <li><a href="/main/kickTranscriber/getTodoFromDb">  transcriber.getTodoFromDb(True) </a></li>
        </ul>

    <hr/>

    <ul>
        <li> test </li>
        <ul> 
            <li><a href="/yo">/yo (Hello World)</a></li>
            <li><a href="/test/yt1"> /test/yt1 hard coded (get meta)  </a></li>
            <li><a href="/test/yt2"> /test/yt2 hard coded (dl from arr of vids) </a></li>
            <li><a href="/test/yt21"> /test/yt2 twitch audio dl low quality </a></li>
            <li><a href="/test/yt3"> /test/yt3 hard coded (dl from arr of vids) </a></li>
            
            <li><a href="/test/doS3Stuff"> /test/doS3Stuff  </a></li>
            <li><a href="/test/uploadJsonToS3Test"> /test/uploadJsonToS3Test (mock json, s3 example) </a></li>
            <li><a href="/test/getAllS3Jsons"> /test/getAllS3Jsons (15+ jsons in s3) </a></li>
            <li><a href="/test/testGetTop500Channels_NameCompleted"> /test/testGetTop500Channels_NameCompleted  </a></li>
        </ul>
        <hr/>

        
    </ul>

    """


if __name__ == "__main__":
    print("RUNNING ON PORT 5000")
    app.run(debug=True, port=5000)


