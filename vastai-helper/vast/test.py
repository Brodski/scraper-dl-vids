import json
import os


def handler(event, context):

    print(f"Received event: {json.dumps(event)}")
    print(f"Received event: {json.dumps(event)}")

    response_message = {
        'message': 'Hello from Lambda! X',
        'input': event
    }

    # Computer -> TF TF_VAR_XXX-> lambda-env-vars XXX -> python
    print(f"Response: {json.dumps(response_message)}")
    api_key3 = os.environ.get('ANOTHER_VARIABLE')
    api_key5 = os.environ.get('MY_VARIABLE')
    print("''''''")
    print("api_key3 ANOTHER_VARIABLE=" + str(api_key3))
    print("api_key5 MY_VARIABLE=" + str(api_key5))
    return response_message

if __name__ == "__main__":
    test_event = {}  # Populate with a sample event if needed
    print(handler(test_event, None))
