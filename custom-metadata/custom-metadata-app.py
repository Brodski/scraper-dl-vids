# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!
# I'M PRETTY SURE THIS IS NOT DOING ANYTHING!!!!!!!!

from flask import Flask, jsonify, request
from dotenv import load_dotenv
import requests
import json
import boto3
import os

load_dotenv()
app = Flask(__name__)

# This is very improper data-storage
#
# Expected request from client:
# {
#   "id": 123 <--- required
#   "channel": lolgeranimo <--- required
#   "date": 1392993234
#   "lang": en 
#    ... anything else
# }
# 
# 

def lambda_handler(event, context):
    return manage_data()

@app.route('/', methods=['GET', 'POST'])
def manage_data():
    BUCKET_NAME = 'my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket'
    BUCKET_DOMAIN = 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com'
    S3_CUSTOM_METADATA_BASE = 'channels/completed-jsons/custom-metadata/'
    
    s3 = boto3.client('s3')
    
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print('os.getenv("CUSTOM_MD_KEY")')
    print(os.getenv("CUSTOM_MD_KEY"))
    print(os.getenv("CUSTOM_MD_KEY"))
    print(os.getenv("CUSTOM_MD_KEY"))
    print(os.getenv("CUSTOM_MD_KEY"))
    
    headerz = request.headers
    if headerz.get('Content-Type') != 'application/json':
        return 'shit failed'
    
    if headerz.get('X-custom-md-key-yeah') != os.getenv("CUSTOM_MD_KEY"):
        return 'shit failed 2'
    post_data = request.get_json()
    vod_id = post_data.get('id')
    channel = post_data.get('channel')
    
    key = S3_CUSTOM_METADATA_BASE + channel + "/custom-metadata.json"

    print(json.dumps(post_data, indent=4))
    print("key=" + key)

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
    s3.put_object(Body=json.dumps(custom_metadata_json_file, default=lambda o: o.__dict__), ContentType="application/json; charset=utf-8", Bucket=BUCKET_NAME, Key=key)

    return 'done'


# @app.route('/post', methods=['GET'])
# def manage_dataz():
#     data = {
#         'id': '1861789415',
#         'channel': 'lolgeranimo',
#         'test': 'test 1 2 3',
#          "display_id":"v1747933567",
#          "fulltitle":"Bootcamp to Challenger |",
#          "duration_string":"5:30:20",
#          "upload_date":"20230224",
#          "epoch":1681813934,
#          "timestamp": 1681813863
#     }

#     headers = {'Content-Type': 'application/json'}
#     response = requests.post('http://localhost:1111/', data=json.dumps(data), headers=headers)
#     return 'donepost'


# @app.route('/post2', methods=['GET'])
# def manage2():
#     data = {
#         'id': '1861789415',
#         'channel': 'lolgeranimo',
#         "isee": "girls",
#         "driving-me": 'crazy'
#     }

#     headers = {'Content-Type': 'application/json'}
#     response = requests.post('http://localhost:1111/', data=json.dumps(data), headers=headers)
#     return 'donepost'


# @app.route('/post3', methods=['GET'])
# def manage3():
#     data = {
#         'id': '1234455557',
#         'channel': 'lolgeranimo',
#         "flo": "rida",
#         "play-my": 'track'
#     }

#     headers = {'Content-Type': 'application/json'}
#     response = requests.post('http://localhost:1111/', data=json.dumps(data), headers=headers)
#     return 'donepost'


if __name__ == '__main__':
    if (os.getenv("IS_LAMBDA") != "true"):
        app.run(debug=True, port=1111)


    # app.run(debug=True, port=1111)

    # else:
    #     console.log("process.env.IS_LAMBDA" , process.env.IS_LAMBDA)
    #     module.exports.handler = serverless(app);
    # }
    # console.log("=========================")