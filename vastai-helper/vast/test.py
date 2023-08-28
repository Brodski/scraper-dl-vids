import json
import os


def handler(event, context):

    print(f"Received event: {json.dumps(event)}")

    response_message = {
        'message': 'Hello from Lambda!',
        'input': event
    }

    # Computer -> TF TF_VAR_XXX-> lambda-env-vars XXX -> python
    print(f"Response: {json.dumps(response_message)}")
    # api_key = os.environ.get ('api_key')
    # api_key2 = os.environ.get('TF_VAR_api_key')
    api_key3 = os.environ.get('ANOTHER_VARIABLE')
    # api_key4 = os.environ.get('TF_VAR_ANOTHER_VARIABLE')
    api_key5 = os.environ.get('MY_VARIABLE')
    print("''''''")
    # print("api_key  api_key=" +  str(api_key))
    # print("api_key2 TF_VAR_api_key=" + str(api_key2))
    print("api_key3 ANOTHER_VARIABLE=" + str(api_key3))
    # print("api_key4 TF_VAR_ANOTHER_VARIABLE=" + str(api_key4))
    print("api_key5 MY_VARIABLE=" + str(api_key5))
    return response_message

if __name__ == "__main__":
    test_event = {}  # Populate with a sample event if needed
    print(handler(test_event, None))
