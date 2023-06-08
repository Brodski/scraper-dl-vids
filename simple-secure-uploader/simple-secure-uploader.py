from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload_file():
    # Handle file upload logic here
    file = request.files['file']
    if file:
        # Save or process the file as needed
        file.save('uploaded_file.txt')
        return 'File uploaded successfully.'
    else:
        return 'No file provided.'

if __name__ == '__main__':
    app.run(debug=True)
