from __future__ import unicode_literals
from flask import Flask
from  routes.testz import test_bp
# from bs4 import BeautifulSoup

# import youtube_dl

app = Flask(__name__)
app.register_blueprint(test_bp, url_prefix='/test')

@app.route('/')
def home():
    # Links to all other routes in the app.
    return """
    <h1>Links to all other routes in the app.</h1>
    <ul>
        <li><a href="/yo">/yo (Hello World)</a></li>
        <li><a href="/yt">/yt (downloads a vid)</a></li>
        <li><a href="/yt1">/yt1 (downloads and extract_info a vid) </a></li>
        <li><a href="/download/topics">/download/topic  </a></li>
        <li><a href="/download/date">/download/date  </a></li>
        <li><a href="/test/yt1"> hard coded (dl from arr of vids) </a></li>
        <li><a href="/test/yt2"> hard coded (get meta)  </a></li>
        <hr/>
        <li><a href="/gera">/gera gera stuff RIP </a></li>
        <li><a href="/test">/test (scrapes ycombinator) RIP </a></li>
    </ul>

    """

@app.route('/yo/<text>')
@app.route('/yo/')
def yo(text="brother"):

    return "Yo {} @ {}".format(text, app.root_path)


if __name__ == "__main__":
    app.run(debug=True)


