from flask import Flask, jsonify, request
import requests
import json
import boto3

app = Flask(__name__)

# TODO THIS SHOULD BE A SQL SERVER
# Expected request from client:
# {
#   "id": 123 <--- required
#   "channel": lolgeranimo <--- required
#   "date": 1392993234
#   "lang": en 
# }
# 
# 
@app.route('/', methods=['GET', 'POST'])
def manage_data():
    BUCKET_NAME = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket'
    BUCKET_DOMAIN = 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com'
    S3_CUSTOM_METADATA_BASE = 'channels/completed-jsons/custom-metadata/'
    
    s3 = boto3.client('s3')
    
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxx")
    x = request.headers
    if x.get('Content-Type') != 'application/json':
        return
    print(x)
    post_data = request.get_json()
    print(json.dumps(post_data, indent=4))
    vod_id = post_data.get('id')
    channel = post_data.get('channel')

    key = S3_CUSTOM_METADATA_BASE + channel + "/custom-metadata.json"
    print(key)
    print(key)
    print(key)
    print(key)

    try:
        resS3 = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        custom_metadata_json_file = json.loads(resS3["Body"].read().decode("utf-8"))
    except:
        print("Does not exist")
        custom_metadata_json_file = {}

    print("custom_metadata_s3")
    print(custom_metadata_json_file)

    vod_metadata = custom_metadata_json_file.get(vod_id)

    if not vod_metadata:
        print("NOT!!!!!!!!!")
        vod_metadata = {}
    for k, value in post_data.items():
        print(f'{k}: {value}')
        vod_metadata[k] = value
        # if k == "channel":
        #     continue

    custom_metadata_json_file[vod_id] = vod_metadata
    
    print("custom_metadata")
    print("custom_metadata")
    print("custom_metadata")
    print("custom_metadata")
    print(json.dumps(custom_metadata_json_file , indent=4))
    poop = s3.put_object(Body=json.dumps(custom_metadata_json_file, default=lambda o: o.__dict__), Bucket=BUCKET_NAME, Key=key)

    print ("poop")
    print (poop)
    return 'done'


@app.route('/post', methods=['GET'])
def manage_dataz():
    data = {
        'id': '1861789415',
        'channel': 'lolgeranimo',
        'test': 'test 1 2 3',
         "display_id":"v1747933567",
         "fulltitle":"Bootcamp to Challenger |",
         "duration_string":"5:30:20",
         "upload_date":"20230224",
         "epoch":1681813934,
         "timestamp": 1681813863
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post('http://localhost:1111/', data=json.dumps(data), headers=headers)
    return 'donepost'


@app.route('/post2', methods=['GET'])
def manage2():
    data = {
        'id': '1861789415',
        'channel': 'lolgeranimo',
        "isee": "girls",
        "driving-me": 'crazy'
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post('http://localhost:1111/', data=json.dumps(data), headers=headers)
    return 'donepost'


@app.route('/post3', methods=['GET'])
def manage3():
    data = {
        'id': '1234455557',
        'channel': 'lolgeranimo',
        "flo": "rida",
        "play-my": 'track'
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post('http://localhost:1111/', data=json.dumps(data), headers=headers)
    return 'donepost'


if __name__ == '__main__':
    app.run(debug=True, port=1111)
