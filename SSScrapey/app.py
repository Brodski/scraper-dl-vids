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

        <li><a href="/main/ranking/getTopChannelsAndSave"> /main/ranking/getTopChannelsAndSave </a></li>
        <ul>
            <li><a href="/ranking/getTopChannels"> /ranking/getTopChannels </a></li>
            <li> /ranking/saveTopChannels (dummy) </li>
        </ul>
        <hr/>
        <li> Init Scrape (part 1, find links) </li>
        <li><a href="/main/ytdl/initYtdlAudio"> /main/ytdl/initYtdlAudio </a></li>
        <ul>
            <li><a href="/hrefGet/scrape4VidHref/mock"> /hrefGet/scrape4VidHref/mock </a></li>
            <li> addTodoListS3: /ytdl/addTodoListS3 (dummy) </li>
            <li> bigBoyChannelDownloader: /ytdl/bigBoyChannelDownloader (dummy) </li>
            <ul>
                <li><a href="/ytdl/test/downloadTwtvVid_FIXED"> /ytdl/test/downloadTwtvVid_FIXED(/videos/1231231) </a></li>
                <li> /ytdl/downloadTwtvVid (dummy) </li>
            </ul>
        </ul>
        <li><a href="/s3/syncAudioFilesUploadJsonS3"> audio /s3/syncAudioFilesUploadJsonS3 </a></li>
        <li><a href="/s3/syncCaptionsUploadJsonS3"> captions /s3/syncCaptionsUploadJsonS3 </a></li>
        <li><a href="/s3/_getCompletedJsonSuperS3"> CompS3 /s3/_getCompletedJsonSuperS3 </a></li>
        <ul>
            <li> </li>
        </ul>

        <hr/>



        <li> Init Scrape (part 2, find vids) </li>
        <ul>
            <li><a href="/initScrape/getChannelFromS3"> /initScrape/getChannelFromS3 </a></li>
        </ul>
        


        <li><a href="/ytdl/getAlreadyDownloadedS3_TEST"> /ytdl/getAlreadyDownloadedS3_TEST </a></li>

        <hr/>
    </ul>

    """


if __name__ == "__main__":
    app.run(debug=True)


