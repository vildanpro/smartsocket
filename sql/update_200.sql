UPDATE sockets.messages
SET message_state_id = 21,
    response_code = {response_code},
    response_body = '{response_data}',
    request_date = TO_DATE('{request_date}', 'YYYY-MM-DD HH24:MI:SS'),
    response_date = TO_DATE('{response_date}', 'YYYY-MM-DD HH24:MI:SS')
WHERE message_id = {message_id}