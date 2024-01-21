# import json
#
# def handler(event, context):
#
#     print(f"Received event: {json.dumps(event)}")
#
#     response_message = {
#         'message': 'Hello from Lambda! X',
#         'input': event
#     }
#
#     print(f"Response: {json.dumps(response_message)}")
#     return response_message
#
# if __name__ == "__main__":
#     test_event = {}  # Populate with a sample event if needed
#     print(handler(test_event, None))
