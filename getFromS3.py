import requests
import time

start_time = time.time()


url = 'https://my-bucket-bigger-stronger-faster-richer-than-your-sad-bucket.s3.amazonaws.com/testz/BarbaraWalters.mp3'
response = requests.get(url)
print("got response:" )
print(response)
print(response.status_code)
print()
print("response.content:")
with open('s3333.mp3', 'wb') as f:
    f.write(response.content)

run_time = time.time() - start_time
print(run_time)