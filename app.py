from __future__ import unicode_literals
from flask import Flask
from routes.testz import test_bp
from routes.downloadRoutes import download_bp
# from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort

# import youtube_dl

app = Flask(__name__)
app.register_blueprint(test_bp, url_prefix='/test')
app.register_blueprint(download_bp)

@app.route('/yo/<text>')
@app.route('/yo/')
def yo(text="brother"):

    return "Yo {} @ {}".format(text, app.root_path)


@app.errorhandler(404)
def page_not_found(error):
    response = jsonify({"error": "Resource not found"})
    response.status_code = 404
    return response


@app.errorhandler(400)
def conflict_error(error):
    response = jsonify({"error":  error.description})
    response.status_code = 400
    return response

# @app.errorhandler(Exception)
# def server_error(error):
#     app.logger.exception(error)
#     print ("OOPS! I fucked up!")
#     return "OOPS! I fucked up", 500


@app.route('/')
def home():
    # Links to all other routes in the app.
    return """
    <h1>Links to all other routes in the app.</h1>
    <ul>
        <li><a href="/yo">/yo (Hello World)</a></li>
        <li><a href="/test/yt1"> /test/yt1 hard coded (get meta)  </a></li>
        <li><a href="/test/yt2"> /test/yt2 hard coded (dl from arr of vids) </a></li>
        <li><a href="/channel/lolgeranimo"> /channel/<lolgeranimo>   </a></li>
        <li><a href="/test/doS3Stuff"> /test/doS3Stuff  </a></li>
        <li><a href="/test/uploadJsonToS3Test"> /test/uploadJsonToS3Test (mock json, s3 example) </a></li>
        <li><a href="/test/getAllS3Jsons"> /test/getAllS3Jsons (15+ jsons in s3) </a></li>
        <li><a href="/test/testGetTop500Channels_NameCompleted"> /test/testGetTop500Channels_NameCompleted  </a></li>
        <li><a href="/getTopChannels"> /getTopChannels </a></li>
        <li><a href="/getTopChannelsAndSave"> /getTopChannelsAndSave </a></li>
        <li><a href="/initScrape"> /initScrape </a></li>
        <li><a href="/scrape4HrefAux"> /scrape4HrefAux </a></li>
        <li><a href="/initScrapeHrefs"> /initScrapeHrefs </a></li>
        <hr/>
        <hr/>
        <li><a href="/gera">/gera gera stuff RIP </a></li>
        <li><a href="/test">/test (scrapes ycombinator) RIP </a></li>
    </ul>

    """


if __name__ == "__main__":
    app.run(debug=True)


