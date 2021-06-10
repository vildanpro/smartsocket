from queries import get_new_messages, update_message_if_response_code_200, update_message_if_response_code_408
from device_request import do_device_request


while True:
    messages = get_new_messages()
    for message in messages:
        print('MESSAGE_ID:', message.message_id, 'DEVICE_ID:', message.device_id, 'CREATED:', message.created)
        response = do_device_request(message.uri)
        if response.response_code == 200:
            update_message_if_response_code_200(message.message_id,
                                                response)
        elif response.response_code == 408:
            update_message_if_response_code_408(message_id=message.message_id,
                                                request_date=response.request_date,
                                                response_code=response.response_code)
